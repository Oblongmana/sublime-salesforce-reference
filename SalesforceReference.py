"""SublimeSalesforceReference: Quick access to Salesforce Documentation from Sublime Text"""
__version__ = "1.0.0"
__author__ = "James Hill (oblongmana@gmail.com)"
__copyright__ = "SublimeSalesforceReference: (C) 2014 James Hill. GNU GPL 3."
__credits__ = ["All Salesforce Documentation is © Copyright 2000–2014 salesforce.com, inc."]

import sublime, sublime_plugin
import urllib
import xml.etree.ElementTree as ElementTree
import webbrowser


class SalesforceReferenceCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.retrieve_index_async()
        

    def retrieve_index_async(self):
        sublime.status_message('Retrieving Salesforce Reference Index...')
        sublime.set_timeout_async(self.retrieve_index,0)
    
    def retrieve_index(self):
        sf_xml = urllib.request.urlopen('http://www.salesforce.com/us/developer/docs/apexcode/Data/Toc.xml').read().decode('utf-8')
        sf_tree = ElementTree.fromstring(sf_xml)
        leaf_parents = sf_tree.findall("*[@Title='Reference'].//TocEntry[@DescendantCount='0']..")
        self.sf_ref_pages_titles = []
        self.sf_ref_pages_links = []
        for parent in leaf_parents:
            self.sf_ref_pages_titles.append(parent.attrib['Title'])
            self.sf_ref_pages_links.append(parent.attrib['Link'])

        self.window.show_quick_panel(self.sf_ref_pages_titles, self.open_documentation)

    def open_documentation(self, reference_index):
        if(reference_index != -1):
            base_url= 'http://www.salesforce.com/us/developer/docs/apexcode'
            webbrowser.open_new_tab(base_url + self.sf_ref_pages_links[reference_index])


