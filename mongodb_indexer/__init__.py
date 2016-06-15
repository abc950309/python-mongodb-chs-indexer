import jieba
import re
from tornado_tilimer.multirefs import _multirefs

class _DataBase(object):
    
    def __init__(self):
        pass
    
    def set(self, db):
        self._db = db
    
    def __call__(self):
        return self._db

db = _DataBase()

def set_database(collection):
    
    """设置公用的数据库Collection
   
    :param pymongo.collection.Collection db: APP 使用的 MongoDB Collection.
    """
    
    db.set(collection)

word_re = re.compile(r'^\w+$')

def Indexer(**kwargs):
    
    struct      = kwargs['struct']
    name        = struct._name + '_indexs'
    data_name   = struct._name
    settings    = kwargs['settings']
    
    text_tuple = []
    for key, val in settings.items():
        if val == 'text':
            text_tuple.append(key)
    text_tuple = tuple(text_tuple)
    
    class _indexer(object):
    
        _name       = name
        _data_name  = data_name
        _struct     = struct
        _text_tuple = text_tuple
        
        @classmethod
        def update(cls, data):
            if hasattr(data, 'tornado_tilimer_datas_signal'):
                data = data._data
            id = data['_id']
            
            text = {}
            for key, val in data.items():
                if key in cls._text_tuple:
                    for word in jieba.cut_for_search(val):
                        if word_re.fullmatch(word) == None:
                            continue
                        if word in text:
                            text[word] += 1
                        else:
                            text[word] = 1
            
            db()[cls._name].replace_one(
                filter = {'_id': id},
                replacement = {'_id': id, 'text': text},
                upsert = True,
            )

        @classmethod
        def search(cls, query, skip = 0, limit = 0):
            query = ['text.' + word for word in jieba.cut(query) if word_re.fullmatch(word)]
            pipeline = []
            pipeline.append({'$match': {'$or': [{line: {'$exists': True}} for line in query]}})
            pipeline.append({'$project': {'sum': {'$sum': ['$' + line for line in query]}}})
            pipeline.append({'$sort': {'sum': -1}})
            if skip != 0:
                pipeline.append({'$skip': skip})
            if limit != 0:
                pipeline.append({'$limit': limit})

            data = [line['_id'] for line in db()[cls._name].aggregate(pipeline = pipeline)]
            return _multirefs(data, cls._struct.get)
    
    return _indexer
