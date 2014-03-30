"""SublimeSalesforceReference: Quick access to Salesforce Documentation from Sublime Text"""
__version__ = "1.2.0"
__author__ = "James Hill (oblongmana@gmail.com)"
__copyright__ = "SublimeSalesforceReference: (C) 2014 James Hill. GNU GPL 3."
__credits__ = ["All Salesforce Documentation is © Copyright 2000–2014 salesforce.com, inc.", "ThreadProgress.py is under the MIT License, Will Bond <will@wbond.net>, and SalesforceReference.py's RetrieveIndexThread method is a derives in part from code under the same license"]

import sublime, sublime_plugin
import urllib
import xml.etree.ElementTree as ElementTree
import webbrowser
import threading
from .ThreadProgress import ThreadProgress

class SalesforceReferenceCache():
    def __init__(self):
        self.sf_ref_pages_titles = []
        self.sf_ref_pages_links = []    

reference_cache = SalesforceReferenceCache()

def plugin_loaded():
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
        if not (reference_cache.sf_ref_pages_titles and reference_cache.sf_ref_pages_links):
            sf_xml = urllib.request.urlopen('http://www.salesforce.com/us/developer/docs/apexcode/Data/Toc.xml').read().decode('utf-8')
            sf_tree = ElementTree.fromstring(sf_xml)
            leaf_parents = sf_tree.findall("*[@Title='Reference'].//TocEntry[@DescendantCount='0']..")
            for parent in leaf_parents:
                reference_cache.sf_ref_pages_titles.append(parent.attrib['Title'])
                reference_cache.sf_ref_pages_links.append(parent.attrib['Link'])

        if(self.open_when_done):
            self.window.show_quick_panel(reference_cache.sf_ref_pages_titles, self.open_documentation)

    def open_documentation(self, reference_index):
        if(reference_index != -1):
            base_url= 'http://www.salesforce.com/us/developer/docs/apexcode'
            webbrowser.open_new_tab(base_url + reference_cache.sf_ref_pages_links[reference_index])