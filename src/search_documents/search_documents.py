from google.appengine.api import search

class SearchDocument(object):
    def __init__(self, index_name):
        self.index = search.Index(name=index_name)

    def make_document(self, id, fields):
        document = search.Document(doc_id=id, fields=fields)
        self.index.put(document)

    def make_fields(self, kwargs):
        fields = []
        for name, value in kwargs.iteritems():
            if name in self.fields:
                fields.append(self.fields[name](name=name, value=value))
        return fields

    def create(self, id, **kwargs):
        self.make_document(id, self.make_fields(kwargs))


class BoutDocument(SearchDocument):
    def __init__(self):
        self.index_name = 'bouts'
        self.fields = {'name': search.TextField, 'description': search.TextField}
        super(BoutDocument, self).__init__(self.index_name)

#    @classmethod
#    def search(cls):

