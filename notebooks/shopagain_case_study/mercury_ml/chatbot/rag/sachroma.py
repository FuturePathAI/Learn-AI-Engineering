import chromadb

class SAChroma:
    def __init__(self, path):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = None

    def create_collection(self, name):
        self.collection = self.client.create_collection(name)
        return self.collection

    def get_or_create_collection(self, name):
        self.collection = self.client.get_or_create_collection(name)
        return self.collection

    def list_collections(self):
        return self.client.list_collections()

    def delete_collection(self, name):
        self.client.delete_collection(name)

    def reset_database(self):
        self.client.reset()

    def heartbeat(self):
        return self.client.heartbeat()

    def count_items(self):
        if self.collection:
            return self.collection.count()
        return 0

    def add_items(self, embeddings, metadatas, documents, ids):
        self.collection.add(embeddings=embeddings, metadatas=metadatas, documents=documents, ids=ids)

    def update_items(self, embeddings, metadatas, documents, ids):
        self.collection.update(embeddings=embeddings, metadatas=metadatas, documents=documents, ids=ids)

    def upsert_items(self, embeddings, metadatas, documents, ids):
        self.collection.upsert(embeddings=embeddings, metadatas=metadatas, documents=documents, ids=ids)

    def get_items(self, ids):
        return self.collection.get(ids=ids)

    def peek_items(self, count=5):
        return self.collection.peek(count=count)

    def query_items(self, query_embeddings, n_results, where_filter=None):
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results, where=where_filter)

    def delete_items(self, ids):
        self.collection.delete(ids=ids)
    
    def modify_collection(self, new_name):
        self.collection.modify(name=new_name)