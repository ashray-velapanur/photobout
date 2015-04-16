from google.appengine.api import search

class SearchDocument(object):
    def __init__(self, index_name, id, fields):
        self.index = search.Index(name=index_name)
        self.document = self.make_document(id, fields)

    def make_document(self, id, fields):
        document = search.Document(doc_id=id, fields=fields)
        return document

    def put(self):
        self.index.put(self.document)

    def make_fields(self, kwargs):
        fields = []
        for name, value in kwargs.iteritems():
            if name in self._fields:
                fields.append(self._fields[name](name=name, value=value))
        return fields

class BoutDocument(SearchDocument):
    def __init__(self, id, **kwargs):
        self.index_name = 'bouts'
        self._fields = {'name': search.TextField, 'description': search.TextField}
        super(BoutDocument, self).__init__(self.index_name, id, self.make_fields(kwargs))
