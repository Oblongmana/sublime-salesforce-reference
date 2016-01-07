import threading
import urllib.request
import re
from .cache import SalesforceReferenceCacheEntry
# Import BeautifulSoup (scraping library) and html.parser
#  - Necessary, because as at 2015-06-02 Salesforce no longer uses an XML file
#    for generating Table of Contents, so we have to scrape a ToC out of the
#    page itself
#  - NB: attempting to use html5lib was horrible, due to dependence on six,
#    which obstinately refused to work.
#  - Built in html.parser seems perfectly adequate to needs, but if we ever
#    support ST2, we should check for ST2 and use HTMLParser (if BeautifulSoup
#    supports)
#  - NB: bs4 was rebuilt (using 2to3) for Python3; we'd need to include a
#    Python2 build if we ever support ST2
import sys, traceback
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.path.normpath("lib")))
from bs4 import BeautifulSoup
import json
import html.parser

class DocRetrievalStrategy(threading.Thread):
    def __init__(self, window, cache, cache_lock, done_callback):
        """
        :param window:
            An instance of :class:`sublime.Window` that represents the Sublime
            Text window to show the available package list in.
        :cache
            an instance of SalesforceReferenceCache
        :cache_lock
            a threading.Lock to be used when modifying the cache
        :done_callback
            a function to call when the thread is done running. This would
            generally be something like a `Queue` instance's `task_done` method
        """
        self.window = window
        self.cache = cache
        self.cache_lock = cache_lock
        self.done_callback = done_callback
        threading.Thread.__init__(self)

    @property
    def doc_type(self):
        raise NotImplementedError(
                "SalesforceDocRetrievalStrategy is an interface, implementing "
                "classes should override `doc_type` to return an appropriate "
                "string indicating the doc type (e.g. "
                "DocTypeEnum.VISUALFORCE.name) "
            )

    def run(self):
        raise NotImplementedError(
                "SalesforceDocRetrievalStrategy is an interface, implementing "
                "classes should override `run` to do the appropriate scraping "
                "of required documentation, and cache population "
            )

    def logRetrievalException(self):
        print("######### Sublime Salesforce Reference Error #########")
        print("Fatal error in Sublime Salesforce Reference while retrieving doc. Please report this on https://github.com/Oblongmana/sublime-salesforce-reference/issues. Error info follows:")
        print(traceback.format_exc())
        with self.cache_lock:
            self.cache.append(
                SalesforceReferenceCacheEntry(
                    'Error retrieving doc. Press Cmd/Ctrl+` for details, and report the error on github',
                    '',
                    self.doc_type
                )
            )

class ApexDocJsonTocBasedStrategy(DocRetrievalStrategy):
    def __init__(self, window, cache, cache_lock, done_callback):
        DocRetrievalStrategy.__init__(self, window, cache, cache_lock, done_callback)

    @property
    def doc_type(self):
        return DocTypeEnum.APEX.name

    def run(self):
        try:
            sf_document = urllib.request.urlopen(urllib.request.Request(DocTypeEnum.APEX.toc_url,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
            sf_json = json.loads(sf_document)
            sf_toc = sf_json["toc"]
            reference_toc = filter(lambda x: "id" in x and x["id"] == "apex_reference", sf_toc)
            for toc_entry in getAllTocLeafParents(next(reference_toc),None):
                with self.cache_lock:
                    self.cache.append(
                        SalesforceReferenceCacheEntry(
                            toc_entry["text"],
                            toc_entry["a_attr"]["href"],
                            DocTypeEnum.APEX.name
                        )
                    )
        except Exception as e:
            self.logRetrievalException();

        self.done_callback()

class VisualforceDocJsonTocBasedStrategy(DocRetrievalStrategy):
    def __init__(self, window, cache, cache_lock, done_callback):
        DocRetrievalStrategy.__init__(self, window, cache, cache_lock, done_callback)

    @property
    def doc_type(self):
        return DocTypeEnum.VISUALFORCE.name

    def run(self):
        try:
            # TODO: basically a replica of Apex, but with diff DocTypeEnum and "id" being searched for. Could use DRYing
            sf_document = urllib.request.urlopen(urllib.request.Request(DocTypeEnum.VISUALFORCE.toc_url,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
            sf_json = json.loads(sf_document)
            sf_toc = sf_json["toc"]
            reference_toc = filter(lambda x: "id" in x and x["id"] == "pages_compref", sf_toc)
            for toc_entry in getAllTocLeaves(next(reference_toc)):
                with self.cache_lock:
                    self.cache.append(
                        SalesforceReferenceCacheEntry(
                            toc_entry["text"],
                            toc_entry["a_attr"]["href"],
                            DocTypeEnum.VISUALFORCE.name
                        )
                    )
        except Exception as e:
            self.logRetrievalException();

        self.done_callback()

class ServiceConsoleDocJsonTocBasedStrategy(DocRetrievalStrategy):
    def __init__(self, window, cache, cache_lock, done_callback):
        DocRetrievalStrategy.__init__(self, window, cache, cache_lock, done_callback)

    @property
    def doc_type(self):
        return DocTypeEnum.SERVICECONSOLE.name

    def run(self):
        try:
            # TODO: has similarities to Apex/VF, but with diff DocTypeEnum, "text" being searched for (whereas others search on "id"), and the fact there are multiple "root" nodes for the ToC (one for each "Methods for" section). Could use DRYing maybe? Possibly not
            sf_document = urllib.request.urlopen(urllib.request.Request(DocTypeEnum.SERVICECONSOLE.toc_url,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
            sf_json = json.loads(sf_document)
            sf_toc = sf_json["toc"]
            for methods_toc in filter(lambda x: "id" in x and x["text"].startswith("Methods for"), sf_toc):
                for toc_entry in getAllTocLeaves(methods_toc):
                    with self.cache_lock:
                        self.cache.append(
                            SalesforceReferenceCacheEntry(
                                toc_entry["text"],
                                toc_entry["a_attr"]["href"],
                                DocTypeEnum.SERVICECONSOLE.name
                            )
                        )
        except Exception as e:
            self.logRetrievalException();

        self.done_callback()

def getAllTocLeafParents(toc,parent):
    try:
        for child in toc["children"]:
            for leaf_parent in getAllTocLeafParents(child,toc):
                yield leaf_parent
    except KeyError:
        yield parent

def getAllTocLeaves(toc):
    try:
        for child in toc["children"]:
            for leaf in getAllTocLeaves(child):
                yield leaf
    except KeyError:
        yield toc

class DocType:
    def __init__(self, name, doc_base_url, toc_url, preferred_strategy):
        self.__name = name
        self.__doc_base_url = doc_base_url
        self.__toc_url = toc_url
        self.__preferred_strategy = preferred_strategy
    @property
    def name(self):
        return self.__name
    @property
    def doc_base_url(self):
        return self.__doc_base_url
    @property
    def toc_url(self):
        return self.__toc_url
    @property
    def preferred_strategy(self):
        return self.__preferred_strategy

class DocTypeEnum:
    VISUALFORCE = DocType(
            "VISUALFORCE",
            "https://developer.salesforce.com/docs/atlas.en-us.pages.meta/pages/",
            "https://developer.salesforce.com/docs/get_document/atlas.en-us.pages.meta",
            VisualforceDocJsonTocBasedStrategy
        )
    APEX = DocType(
            "APEX",
            "https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/",
            "https://developer.salesforce.com/docs/get_document/atlas.en-us.apexcode.meta",
            ApexDocJsonTocBasedStrategy
        )
    SERVICECONSOLE = DocType(
            "SERVICECONSOLE",
            "https://developer.salesforce.com/docs/atlas.en-us.api_console.meta/api_console/",
            "https://developer.salesforce.com/docs/get_document/atlas.en-us.api_console.meta",
            ServiceConsoleDocJsonTocBasedStrategy
        )
    @staticmethod
    def get_all():
        return [
            DocTypeEnum.VISUALFORCE,
            DocTypeEnum.APEX,
            DocTypeEnum.SERVICECONSOLE
        ]
    @staticmethod
    def get_by_name(name):
        if name == DocTypeEnum.VISUALFORCE.name:
            return DocTypeEnum.VISUALFORCE
        elif name == DocTypeEnum.APEX.name:
            return DocTypeEnum.APEX
        elif name == DocTypeEnum.SERVICECONSOLE.name:
            return DocTypeEnum.SERVICECONSOLE
