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
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.path.normpath("lib")))
from bs4 import BeautifulSoup
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


class ApexDocScrapingStrategy(DocRetrievalStrategy):
    def __init__(self, window, cache, cache_lock, done_callback):
        DocRetrievalStrategy.__init__(self, window, cache, cache_lock, done_callback)

    @property
    def doc_type(self):
        return DocTypeEnum.APEX.name

    def run(self):
        sf_html = urllib.request.urlopen(urllib.request.Request(DocTypeEnum.APEX.url,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
        page_soup = BeautifulSoup(sf_html, "html.parser")
        reference_soup = page_soup.find_all(text="Reference",class_="toc-text")[0].parent.parent.next_sibling
        leaf_soup_list = reference_soup.find_all(class_="leaf")
        header_soup_list = map(lambda leaf: leaf.parent.previous_sibling,leaf_soup_list)
        unique_header_soup_list = list()
        for header_soup in header_soup_list:
            if header_soup not in unique_header_soup_list:
                unique_header_soup_list.append(header_soup)
                header_data_tag = header_soup.find(class_="toc-a-block")
                with self.cache_lock:
                    self.cache.append(
                        SalesforceReferenceCacheEntry(
                            header_data_tag.find(class_="toc-text").string,
                            header_data_tag["href"],
                            DocTypeEnum.APEX.name
                        )
                    )
        self.done_callback()

class VisualforceDocScrapingStrategy(DocRetrievalStrategy):
    def __init__(self, window, cache, cache_lock, done_callback):
        DocRetrievalStrategy.__init__(self, window, cache, cache_lock, done_callback)

    @property
    def doc_type(self):
        return DocTypeEnum.VISUALFORCE.name

    def run(self):
        sf_html = urllib.request.urlopen(urllib.request.Request(DocTypeEnum.VISUALFORCE.url,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
        page_soup = BeautifulSoup(sf_html, "html.parser")
        reference_soup = page_soup.find_all(text="Standard Component Reference",class_="toc-text")[0].parent.parent.parent
        span_list = reference_soup.find_all("span", class_="toc-text")
        for span in span_list:
            link = span.parent
            with self.cache_lock:
                self.cache.append(
                        SalesforceReferenceCacheEntry(
                            span.string,
                            link["href"],
                            DocTypeEnum.VISUALFORCE.name
                        )
                    )
        self.done_callback()

class ServiceConsoleDocScrapingStrategy(DocRetrievalStrategy):
    def __init__(self, window, cache, cache_lock, done_callback):
        DocRetrievalStrategy.__init__(self, window, cache, cache_lock, done_callback)

    @property
    def doc_type(self):
        return DocTypeEnum.SERVICECONSOLE.name

    def run(self):
        sf_html = urllib.request.urlopen(urllib.request.Request(DocTypeEnum.SERVICECONSOLE.url,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
        page_soup = BeautifulSoup(sf_html, "html.parser")
        reference_soup = page_soup.find_all("span", text=re.compile("Methods for \w"), class_="toc-text")
        for reference in reference_soup:
            span_list = reference.parent.parent.parent.find_all("span", class_="toc-text", text=re.compile("^(?!Methods for)"))
            for span in span_list:
                link = span.parent
                with self.cache_lock:
                    self.cache.append(
                        SalesforceReferenceCacheEntry(
                            span.string,
                            link["href"],
                            DocTypeEnum.SERVICECONSOLE.name
                        )
                    )
        self.done_callback()

class DocType:
    def __init__(self, name, url, preferred_strategy):
        self.__name = name
        self.__url = url
        self.__preferred_strategy = preferred_strategy
    @property
    def name(self):
        return self.__name
    @property
    def url(self):
        return self.__url
    @property
    def preferred_strategy(self):
        return self.__preferred_strategy

class DocTypeEnum:
    VISUALFORCE = DocType(
            "VISUALFORCE",
            "http://developer.salesforce.com/docs/atlas.en-us.pages.meta/pages/",
            VisualforceDocScrapingStrategy
        )
    APEX = DocType(
            "APEX",
            "http://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/",
            ApexDocScrapingStrategy
        )
    SERVICECONSOLE = DocType(
            "SERVICECONSOLE",
            "http://developer.salesforce.com/docs/atlas.en-us.api_console.meta/api_console/",
            ServiceConsoleDocScrapingStrategy
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
