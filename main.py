import requests
from inmemorydb import InMemoryVectorDB

memorydb = InMemoryVectorDB()
collection = memorydb.get_or_create_collection("example")

url = "https://api.frankfurter.app/latest"
response = requests.get(url)
api_data = response.json()

currencies = list(api_data['rates'].keys())

dates = ['2024-03-15', '2024-03-16', '2024-03-17']

def fetch_conversion_rates(date, currencies):
    rates = {}
    try:
        response = requests.get(f'https://api.frankfurter.app/{date}')
        data = response.json()
        rates = {curr: data['rates'].get(curr, 'N/A') for curr in currencies}
    except Exception as e:
        print(f"Error fetching conversion rates for {date}: {e}")
    return rates

documents = []
metadatas = []
ids = []

for date in dates:
    rates = fetch_conversion_rates(date, currencies)
    for currency, rate in rates.items():
        document = f"EUR to {currency} conversion rate is {rate} on {date}"
        documents.append(document)
        metadata = {"base": "EUR", "target": currency, "date": date, "rate": rate}
        id_ = f"EUR-{currency}-{date.replace('-', '')}"
        metadatas.append(metadata)
        ids.append(id_)

# Tokenization and Vocabulary Building
def tokenize_documents(docs):
    vocabulary = set()
    tokenized_docs = [doc.lower().split() for doc in docs]
    for doc in tokenized_docs:
        vocabulary.update(doc)
    vocabulary = sorted(list(vocabulary))
    return tokenized_docs, vocabulary

def vectorize_documents(docs, vocab):
    vectors = []
    vocab_index = {word: idx for idx, word in enumerate(vocab)}
    for doc in docs:
        vector = [0] * len(vocab)
        for word in doc:
            if word in vocab_index:
                vector[vocab_index[word]] += 1
        vectors.append(vector)
    return vectors

tokenized_documents, vocabulary = tokenize_documents(documents)
bow_embeddings = vectorize_documents(tokenized_documents, vocabulary)

collection.add(
    embeddings=bow_embeddings,
    metadatas=metadatas,
    documents=documents,
    ids=ids,
)

# Search
search_query = "EUR to INR conversion rate on 17-03-2024"
tokenized_query, _ = tokenize_documents([search_query])
query_embeddings = vectorize_documents(tokenized_query, vocabulary)

results = collection.query(
    query_embeddings=query_embeddings,
    include=["documents", "metadatas"]
)

print(results)
