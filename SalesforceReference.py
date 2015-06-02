"""SublimeSalesforceReference: Quick access to Salesforce Documentation from Sublime Text"""
__version__ = "1.2.0"
__author__ = "James Hill (oblongmana@gmail.com)"
__copyright__ = "SublimeSalesforceReference: (C) 2014-2015 James Hill. GNU GPL 3."
__credits__ = ["All Salesforce Documentation is © Copyright 2000–2015 salesforce.com, inc.", "ThreadProgress.py is under the MIT License, Will Bond <will@wbond.net>, and SalesforceReference.py's RetrieveIndexThread method is a derives in part from code under the same license"]

import sublime, sublime_plugin
import urllib
import xml.etree.ElementTree as ElementTree
import webbrowser
import threading
import collections
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

SALESFORCE_DOC_URL_BASE = 'http://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/'

class SalesforceReferenceCache(collections.MutableSequence):
    """
    A cache of SalesforceReferenceEntry objects, sorted by Title. This order
    will be maintained throughout append operations
    """
    def __init__(self, *data):
        self.entries = list(data)
        self.__sort_by_title()
        self.__determine_titles()
    @property
    def titles(self):
        return self.__titles
    def __getitem__(self, key):
        return self.entries[key]
    def __setitem__(self, key, value):
        self.entries[key] = value
        self.__sort_by_title()
        self.__determine_titles()
    def __delitem__(self, key):
        del self.entries[key]
        self.__determine_titles()
    def __len__(self):
        return len(self.entries)
    def __sort_by_title(self):
        self.entries.sort(key=lambda cacheEntry: cacheEntry.title)
    def insert(self, key,val):
        self.entries.insert(key,val)
        self.__sort_by_title()
        self.__determine_titles()
    def __determine_titles(self):
        self.__titles = list(map(lambda entry: entry.title,self.entries))
    """str and repr implemented for debugging"""
    def __str__(self):
        return str(self.entries)
    def __repr__(self):
        return repr(self.entries)

class SalesforceReferenceCacheEntry(object):
    def __init__(self,title,url):
        self.title = title
        self.url = url
    """str and repr implemented for debugging"""
    def __str__(self):
        return str({'title':self.title,'url':self.url})
    def __repr__(self):
        return str({'title':self.title,'url':self.url})



reference_cache = SalesforceReferenceCache()


def plugin_loaded():
    settings = sublime.load_settings("SublimeSalesforceReference.sublime-settings")
    if settings != None and settings.get("refreshCacheOnLoad") == True:
        thread = RetrieveIndexThread(sublime.active_window(),False)
        thread.start()
        ThreadProgress(thread, 'Retrieving Salesforce Reference Index...', '')


class SalesforceReferenceCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = RetrieveIndexThread(self.window)
        thread.start()
        ThreadProgress(thread, 'Retrieving Salesforce Reference Index...', '')


class RetrieveIndexThread(threading.Thread):
    """
    A thread to run retrieval of the Saleforce Documentation index, or access the reference_cache
    """

    def __init__(self, window, open_when_done=True):
        """
        :param window:
            An instance of :class:`sublime.Window` that represents the Sublime
            Text window to show the available package list in.
        :param open_when_done:
            Whether this thread is being run solely for caching, or should open
            the documentation list for user selection when done. Defaults to
            true - should open the documentaton list when done
        """
        self.window = window
        self.open_when_done = open_when_done
        global reference_cache
        threading.Thread.__init__(self)

    def run(self):
        if not (reference_cache.entries):
            sf_html = urllib.request.urlopen(urllib.request.Request(SALESFORCE_DOC_URL_BASE,None,{'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
            page_soup = BeautifulSoup(sf_html, 'html.parser')
            reference_soup = page_soup.find_all(text='Reference',class_='toc-text')[0].parent.parent.next_sibling
            leaf_soup_list = reference_soup.find_all(class_='leaf')
            header_soup_list = map(lambda leaf: leaf.parent.previous_sibling,leaf_soup_list)
            unique_header_soup_list = list()
            for header_soup in header_soup_list:
                if header_soup not in unique_header_soup_list:
                    unique_header_soup_list.append(header_soup)
                    header_data_tag = header_soup.find(class_='toc-a-block')
                    reference_cache.append(
                        SalesforceReferenceCacheEntry(
                            header_data_tag.find(class_='toc-text').string,
                            header_data_tag['href']
                        )
                    )
        if(self.open_when_done):
            self.window.show_quick_panel(reference_cache.titles, self.open_documentation)

    def open_documentation(self, reference_index):
        if(reference_index != -1):
            base_url= 'http://www.salesforce.com/us/developer/docs/apexcode'
            webbrowser.open_new_tab(SALESFORCE_DOC_URL_BASE + reference_cache[reference_index].url)
