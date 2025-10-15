import re
import json
import time
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI
import tiktoken

load_dotenv()

# Set up pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(host=os.getenv('INDEX_HOST'))

# Set up OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "text-embedding-3-small"
encoding = tiktoken.encoding_for_model(MODEL)


def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def chunk_text(text, max_chars: int = 1000, overlap: int = 200):

    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:


        # Chunk is under the max char size, add to the current chunk
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += " " + sentence
        # Chunk is oversized, add to list
        else:
            chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] + " " + sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def token_chunk_text(text, max_tokens=1000, overlap=200):
    tokens = encoding.encode(text)
    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start += max_tokens - overlap

    return chunks


def chunk_documents(documents):

    chunked_documents = []

    for doc in documents:

        # Chunk the document's text
        text = doc.get("content", "")
        text_chunks = token_chunk_text(text)

        for i, chunk in enumerate(text_chunks):

            if not chunk.strip():
                continue

            # Add to the chunked_documents dictionary
            chunked_documents.append({
                "id": doc.get("url", "") + f"#chunk{i}",
                "text": chunk,
                "title": doc.get("title", ""),
                "category": doc.get("category", "miscellaneous"),
                "document_url": doc.get("url", ""),
            })

    return chunked_documents


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def create_token_safe_batches(chunks, max_tokens=8191):
    batches = []
    current_batch = []
    current_tokens = 0

    for chunk in chunks:
        tokens = count_tokens(chunk['text'])

        # If adding this chunk exceeds limit, start a new batch
        if current_tokens + tokens > max_tokens and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

        # If chunk itself exceeds limit, put it in its own batch
        if tokens > max_tokens:
            print(f"Chunk {chunk['id']} exceeds token limit ({tokens} tokens)")
            batches.append([chunk])
            continue

        current_batch.append(chunk)
        current_tokens += tokens

    if current_batch:
        batches.append(current_batch)

    return batches


def embed_and_upsert(chunked_documents):
    
    batches = create_token_safe_batches(chunked_documents)
    total_batches = len(batches)

    # Separate into batches
    for batch_num, batch in enumerate(batches, start=1):
        texts = [chunk['text'] for chunk in batch]

        print(f"embedding batch #{batch_num} out of {total_batches}")

        try:
            response = client.embeddings.create(
                input=texts,
                model=MODEL
            )
            embeddings = [d.embedding for d in response.data]

        except Exception as e:
            print(f"Error embedding batch {batch_num}: {e}")
            continue

        to_upsert = [
            {
                'id': chunk.get('id'),
                'values': embedding,
                'metadata': {
                    'title': chunk.get('title', ''),
                    'text': chunk.get('text', ''),
                    'category': chunk.get('category', ''),
                    'document_url': chunk.get('document_url', '')
                }
            } for chunk, embedding in zip(batch, embeddings) 
        ]

        print(f"upserting batch #{batch_num} out of {total_batches}")

        try:
            index.upsert(
                vectors=to_upsert,
                namespace='__default__',
            )
        except Exception as e:
            print(f"Error uploading batch {batch_num}: {e}")

        time.sleep(0.05)


def upsert_chunks(chunked_documents, batch_size=96):

    # Separate into batches
    for i in range(0, len(chunked_documents), batch_size):
        print(f"upserting batch #{int(i/batch_size)+1} out of {int(len(chunked_documents)/batch_size)}")
        batch = chunked_documents[i:i+batch_size]

        try:
            # Upsert chunks to database
            index.upsert_records(
                '__default__',
                records=batch
            )
        except Exception as e:
            print(f"Error uploading batch {i // batch_size + 1}: {e}")

        time.sleep(5)


print("loading data...")
docs = load_json('./data/documents.json')
print("finished loading data")
print()
print("chunking docs...")
chunks = chunk_documents(docs)
print("finished chunking docs")
print()
print(len(chunks))
print("upserting and embedding...")
embed_and_upsert(chunks)
print("completed")
print(index.describe_index_stats())