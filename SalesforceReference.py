"""SublimeSalesforceReference: Quick access to Salesforce Documentation from Sublime Text"""
__version__ = "1.4.0"
__author__ = "James Hill (oblongmana@gmail.com)"
__copyright__ = "SublimeSalesforceReference: (C) 2014-2015 James Hill. GNU GPL 3."
__credits__ = ["All Salesforce Documentation is © Copyright 2000–2015 salesforce.com, inc.", "ThreadProgress.py is under the MIT License, Will Bond <will@wbond.net>, and SalesforceReference.py's RetrieveIndexThread method is a derives in part from code under the same license"]

import sublime, sublime_plugin
import urllib.request
import webbrowser
import threading
import re
from .salesforce_reference.cache import SalesforceReferenceCache,SalesforceReferenceCacheEntry
from .ThreadProgress import ThreadProgress

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
sys.path.append(os.path.join(os.path.dirname(__file__), os.path.normpath("lib")))
from bs4 import BeautifulSoup
import html.parser

#These are Salesforce official documentation links
SALESFORCE_APEX_DOC_URL_BASE = "http://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/"
SALESFORCE_VISUALFORCE_DOC_URL_BASE = "http://developer.salesforce.com/docs/atlas.en-us.pages.meta/pages/"
SALESFORCE_SERVICECONSOLE_DOC_URL_BASE = "http://developer.salesforce.com/docs/atlas.en-us.api_console.meta/api_console/"

#These are available documentation type
VISUALFORCE = "visualforce"
APEX = "apex"
SERVICECONSOLE = "serviceconsole"

#Store all reference entries
reference_cache = SalesforceReferenceCache()

def plugin_loaded():
    # Get settings
    global settings
    settings = sublime.load_settings("SublimeSalesforceReference.sublime-settings")
    if settings != None and settings.get("refreshCacheOnLoad") == True:
        thread = RetrieveIndexThread(sublime.active_window(), "all", False)
        thread.start()
        ThreadProgress(thread, "Retrieving Salesforce Reference Index...", "")

# Command to retrieve Apex reference
class SalesforceApexReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = RetrieveIndexThread(self.window, APEX)
        thread.start()
        ThreadProgress(thread, "Retrieving Salesforce Apex Reference Index...", "")

# Command to retrieve Visualforce reference
class SalesforceVisualforceReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = RetrieveIndexThread(self.window, VISUALFORCE)
        thread.start()
        ThreadProgress(thread, "Retrieving Salesforce Visualforce Reference Index...", "")

# Command to retrieve Service Console reference
class SalesforceServiceConsoleReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = RetrieveIndexThread(self.window, SERVICECONSOLE)
        thread.start()
        ThreadProgress(thread, "Retrieving Salesforce Service Console Reference Index...", "")

# Command to retrieve all references specified in settings file
class SalesforceAllReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = RetrieveIndexThread(self.window, "all")
        thread.start()
        ThreadProgress(thread, "Retrieving Salesforce Reference Index...", "")

# Thread that actually download specified reference
class RetrieveIndexThread(threading.Thread):
    """
    A thread to run retrieval of the Saleforce Documentation index, or access the reference_cache
    """

    def __init__(self, window, doc_type, open_when_done=True):
        """
        :param window:
            An instance of :class:`sublime.Window` that represents the Sublime
            Text window to show the available package list in.
        :param doc_type:
            Specify what kind of documentation to retrieve. Accepted values are:
                apex, retrive only apex reference entries
                visualforce, retrieve only visualforce entries
                serviceconsole, retrieve only service console entries
                all, retrieve references specified in Settings file
        :param open_when_done:
            Whether this thread is being run solely for caching, or should open
            the documentation list for user selection when done. Defaults to
            true - should open the documentaton list when done
        """
        self.window = window
        self.doc_type = doc_type
        self.open_when_done = open_when_done
        global reference_cache
        threading.Thread.__init__(self)

    def run(self):
        #Check if has to get APEX doc entries
        if self.doc_type == APEX or (self.doc_type == "all" and settings.get("apexDoc") == True):
            if not reference_cache.entries_by_doc_type.get(APEX):
                self.__get_apex_doc()

        #Check if has to get Visualforce doc entries
        print((self.doc_type == "all" and settings.get("visualforceDoc") == True))
        if self.doc_type == VISUALFORCE or (self.doc_type == "all" and settings.get("visualforceDoc") == True):
            print(str(reference_cache.entries_by_doc_type))
            if not reference_cache.entries_by_doc_type.get(VISUALFORCE):
                self.__get_visualforce_doc()

        #Check if has to get Service Console doc entries
        if self.doc_type == SERVICECONSOLE or (self.doc_type == "all" and settings.get("serviceConsoleDoc") == True):
            if not reference_cache.entries_by_doc_type.get(SERVICECONSOLE):
                self.__get_serviceconsole_doc();

        if(self.open_when_done):
            #Check what kind of docs has to show
            if (self.doc_type == "all"):
                self.window.show_quick_panel(reference_cache.titles, self.open_documentation)
            elif (self.doc_type == APEX):
                self.window.show_quick_panel(reference_cache.titles_by_doc_type.get(APEX), self.open_documentation)
            elif (self.doc_type == VISUALFORCE):
                self.window.show_quick_panel(reference_cache.titles_by_doc_type.get(VISUALFORCE), self.open_documentation)
            elif (self.doc_type == SERVICECONSOLE):
                self.window.show_quick_panel(reference_cache.titles_by_doc_type.get(SERVICECONSOLE), self.open_documentation)

    #Download SERVICE CONSOLE integration toolkit doc entries
    def __get_serviceconsole_doc(self):
        sf_html = urllib.request.urlopen(urllib.request.Request(SALESFORCE_SERVICECONSOLE_DOC_URL_BASE,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
        page_soup = BeautifulSoup(sf_html, "html.parser")
        reference_soup = page_soup.find_all("span", text=re.compile("Methods for \w"), class_="toc-text")
        for reference in reference_soup:
            span_list = reference.parent.parent.parent.find_all("span", class_="toc-text", text=re.compile("^(?!Methods for)"))
            for span in span_list:
                link = span.parent
                reference_cache.append(
                    SalesforceReferenceCacheEntry(
                        span.string,
                        link["href"],
                        SERVICECONSOLE
                    )
                )

    #Download VISUALFORCE doc entries
    def __get_visualforce_doc(self):
        sf_html = urllib.request.urlopen(urllib.request.Request(SALESFORCE_VISUALFORCE_DOC_URL_BASE,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
        page_soup = BeautifulSoup(sf_html, "html.parser")
        reference_soup = page_soup.find_all(text="Standard Component Reference",class_="toc-text")[0].parent.parent.parent
        span_list = reference_soup.find_all("span", class_="toc-text")
        for span in span_list:
            link = span.parent
            reference_cache.append(
                    SalesforceReferenceCacheEntry(
                        span.string,
                        link["href"],
                        VISUALFORCE
                    )
                )

    #Download APEX doc entries
    def __get_apex_doc(self):
        sf_html = urllib.request.urlopen(urllib.request.Request(SALESFORCE_APEX_DOC_URL_BASE,None,{"User-Agent": "Mozilla/5.0"})).read().decode("utf-8")
        page_soup = BeautifulSoup(sf_html, "html.parser")
        reference_soup = page_soup.find_all(text="Reference",class_="toc-text")[0].parent.parent.next_sibling
        leaf_soup_list = reference_soup.find_all(class_="leaf")
        header_soup_list = map(lambda leaf: leaf.parent.previous_sibling,leaf_soup_list)
        unique_header_soup_list = list()
        for header_soup in header_soup_list:
            if header_soup not in unique_header_soup_list:
                unique_header_soup_list.append(header_soup)
                header_data_tag = header_soup.find(class_="toc-a-block")
                reference_cache.append(
                    SalesforceReferenceCacheEntry(
                        header_data_tag.find(class_="toc-text").string,
                        header_data_tag["href"],
                        APEX
                    )
                )

    def open_documentation(self, reference_index):
        url = ""
        if(reference_index != -1):
            if self.doc_type == APEX:
                entry = reference_cache.apexEntries[reference_index]
            elif self.doc_type == VISUALFORCE:
                entry = reference_cache.visualforceEntries[reference_index]
            elif self.doc_type == SERVICECONSOLE:
                entry = reference_cache.serviceconsoleEntries[reference_index]
            elif self.doc_type == "all":
                entry = reference_cache[reference_index]

            if entry:
                if entry.doc_type == APEX:
                    url = SALESFORCE_APEX_DOC_URL_BASE + entry.url
                elif entry.doc_type == VISUALFORCE:
                    url = SALESFORCE_VISUALFORCE_DOC_URL_BASE + entry.url
                elif entry.doc_type == SERVICECONSOLE:
                    url = SALESFORCE_SERVICECONSOLE_DOC_URL_BASE + entry.url

            if url:
                webbrowser.open_new_tab(url)
