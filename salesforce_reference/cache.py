import collections
from functools import total_ordering

class SalesforceReferenceCache(collections.MutableSequence):
    """
    A cache of SalesforceReferenceEntry objects, sorted by Title. This order
    will be maintained throughout append operations
    """
    def __init__(self, *data):
        self.__entries = list(data)
        self.__entries_by_doc_type = {}
        self.__titles_by_doc_type = {}
        self.__maintain_cache()

    # Properties for quick access to cached info

    @property
    def entries(self):
        return self.__entries

    @property
    def titles(self):
        return self.__titles

    @property
    def titles_by_doc_type(self):
        return self.__titles_by_doc_type

    @property
    def entries_by_doc_type(self):
        return self.__entries_by_doc_type

    def __getitem__(self, key):
        return self.__entries[key]
    def __setitem__(self, key, value):
        self.__entries[key] = value
        self.__maintain_cache()
    def __delitem__(self, key):
        del self.__entries[key]
        self.__maintain_cache()
    def __len__(self):
        return len(self.__entries)
    def insert(self, key,val):
        self.__entries.insert(key,val)
        self.__maintain_cache()
    def __maintain_cache(self):
        self.__entries.sort()
        self.__index_entries_by_doc_type()
        self.__index_titles_by_doc_type()
        self.__determine_titles()
    def __index_entries_by_doc_type(self):
        self.__entries_by_doc_type = {title_key: sorted(list(entry))
                                        for title_key, entry in self.__groupby(sorted(self.__entries),lambda entry: entry.doc_type)}
    def __extract_titles_from_list(self,the_list):
        return list(map(lambda entry: entry.title,the_list))
    def __determine_titles(self):
        self.__titles = self.__extract_titles_from_list(self.__entries)
    def __index_titles_by_doc_type(self):
        self.__titles_by_doc_type = {title_key: self.__extract_titles_from_list(sorted(list(entry)))
                                     for title_key, entry in self.__groupby(sorted(self.__entries),lambda entry: entry.doc_type)}
    def __groupby(self, the_list, key=lambda x: x):
        # From http://stackoverflow.com/a/15250161/157556
        # itertools.groupby didn't play nice with custom sorting
        d = collections.defaultdict(list)
        for item in the_list:
            d[key(item)].append(item)
        return d.items()

    """str and repr implemented for debugging"""
    def __str__(self):
        return str(self.__entries)
    def __repr__(self):
        return repr(self.__entries)

@total_ordering
class SalesforceReferenceCacheEntry(object):
    def __init__(self,title,url,doc_type):
        self.title = title
        self.url = url
        self.doc_type = doc_type
    """required functions for use with sort() and sorted()"""
    """the total_ordering annotation supplies remaining comparison functions"""
    def __eq__(self, other):
        return ((self.title.lower(), self.doc_type.lower()) ==
                (other.title.lower(), other.doc_type.lower()))
    def __lt__(self, other):
        return ((self.title.lower(), self.doc_type.lower()) <
                (other.title.lower(), other.doc_type.lower()))
    """str and repr implemented for debugging"""
    def __str__(self):
        return str({"title":self.title,"url":self.url,"doc_type":self.doc_type})
    def __repr__(self):
        return str({"title":self.title,"url":self.url,"doc_type":self.doc_type})
