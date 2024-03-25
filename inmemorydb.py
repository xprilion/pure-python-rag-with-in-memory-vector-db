class InMemoryVectorDB:
    def __init__(self):
        self.collections = {}

    def get_or_create_collection(self, name):
        if name not in self.collections:
            self.collections[name] = Collection()
        return self.collections[name]

class Collection:
    def __init__(self):
        self.embeddings = []
        self.metadatas = []
        self.documents = []
        self.ids = []

    def add(self, embeddings, metadatas, documents, ids):
        self.embeddings.extend(embeddings)
        self.metadatas.extend(metadatas)
        self.documents.extend(documents)
        self.ids.extend(ids)

    def cosine_similarity(self, vec1, vec2):
        dot_product = sum(a*b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a*a for a in vec1) ** 0.5
        magnitude2 = sum(b*b for b in vec2) ** 0.5
        if magnitude1 * magnitude2 == 0:
            return 0
        return dot_product / (magnitude1 * magnitude2)

    def query(self, query_embeddings, include):
        similarities = [self.cosine_similarity(query_embedding, embedding) for query_embedding in query_embeddings for embedding in self.embeddings]
        best_match_index = similarities.index(max(similarities))
        results = {
            'ids': [self.ids[best_match_index]],
            'documents': [self.documents[best_match_index]] if 'documents' in include else [],
            'metadatas': [self.metadatas[best_match_index]] if 'metadatas' in include else []
        }
        return results
