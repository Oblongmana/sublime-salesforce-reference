"""SublimeSalesforceReference: Quick access to Salesforce Documentation from Sublime Text"""
__version__ = "1.1.1"
__author__ = "James Hill (oblongmana@gmail.com)"
__copyright__ = "SublimeSalesforceReference: (C) 2014 James Hill. GNU GPL 3."
__credits__ = ["All Salesforce Documentation is © Copyright 2000–2014 salesforce.com, inc.", "ThreadProgress.py is under the MIT License, Will Bond <will@wbond.net>, and SalesforceReference.py's RetrieveIndexThread method is a derives in part from code under the same license"]

import sublime, sublime_plugin
import urllib
import xml.etree.ElementTree as ElementTree
import webbrowser
import threading
from .ThreadProgress import ThreadProgress

# def plugin_loaded():
#     thread = RetrieveIndexThread(sublime.active_window())
#     thread.start()
#     ThreadProgress(thread, 'Retrieving Salesforce Reference Index...', '')

class SalesforceReferenceCommand(sublime_plugin.WindowCommand):

    def run(self):
        thread = RetrieveIndexThread(self.window)
        thread.start()
        ThreadProgress(thread, 'Retrieving Salesforce Reference Index...', '')


class RetrieveIndexThread(threading.Thread):
    """
    A thread to run retrieval of the Saleforce Documentation induex
    """

    def __init__(self, window):
        """
        :param window:
            An instance of :class:`sublime.Window` that represents the Sublime
            Text window to show the available package list in.
        """

        self.window = window
        threading.Thread.__init__(self)

    def open_documentation(self, reference_index):
        if(reference_index != -1):
            base_url= 'http://www.salesforce.com/us/developer/docs/apexcode'
            webbrowser.open_new_tab(base_url + self.sf_ref_pages_links[reference_index])

    def run(self):
        sf_xml = urllib.request.urlopen('http://www.salesforce.com/us/developer/docs/apexcode/Data/Toc.xml').read().decode('utf-8')
        sf_tree = ElementTree.fromstring(sf_xml)
        leaf_parents = sf_tree.findall("*[@Title='Reference'].//TocEntry[@DescendantCount='0']..")
        self.sf_ref_pages_titles = []
        self.sf_ref_pages_links = []
        for parent in leaf_parents:
            self.sf_ref_pages_titles.append(parent.attrib['Title'])
            self.sf_ref_pages_links.append(parent.attrib['Link'])

        self.window.show_quick_panel(self.sf_ref_pages_titles, self.open_documentation)