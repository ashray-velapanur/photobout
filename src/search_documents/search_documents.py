from google.appengine.api import search

class SearchDocument(object):
	def __init__(self, index_name, id, kwargs):
		self.index = search.Index(name=index_name)
		self.document = self.make_document(id, kwargs)

	def make_document(self, id, kwargs):
		fields = [search.TextField(name=name, value=value) for name, value in kwargs.iteritems()]
		document = search.Document(doc_id=id, fields=fields)
		return document

	def save(self):
		self.index.put(self.document)

class BoutDocument(SearchDocument):
	def __init__(self, id, **kwargs):
		super(BoutDocument, self).__init__('bouts', id, kwargs)

