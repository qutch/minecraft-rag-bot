from openai import OpenAI
import openai
from dotenv import load_dotenv
from pinecone import Pinecone
import os

load_dotenv()

# Set up pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(host=os.getenv('INDEX_HOST'))

# Set up OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = "text-embedding-3-small"
RESPONSE_MODEL = "gpt-5-nano"

# Set up prompt
prompt_template = """
You are an expert Minecraft assistant. Your sole purpose is to answer a user's question about the game clearly and accurately.

You will be given a user's QUESTION and a CONTEXT of retrieved Minecraft Wiki articles. You must adhere to the following rules:

**RULES:**
1.  **Answer the QUESTION using ONLY the information found in the provided CONTEXT.** Do not use any of your internal knowledge or information from your training data. All parts of your answer must be directly supported by the text in the CONTEXT.
2.  **Synthesize the information** from the CONTEXT into a single, coherent, and easy-to-understand answer. Do not just copy and paste sentences from the articles.
3.  **If the CONTEXT does not contain the information** needed to answer the QUESTION, you must respond with: "I'm sorry, but the provided articles don't have the information needed to answer that question."
4.  **Be direct and concise.** Get straight to the point and avoid unnecessary fluff. However, also be somewhat conversational
5.  **Use a friendly and helpful tone,** as if you were another Minecraft player.
6.  **Use markdown formatting** (like bullet points, numbered lists, or bolding key terms) to improve readability, especially for crafting recipes, steps, or lists of items.

---

**CONTEXT:**
{context}

---

**QUESTION:**
{question}

---

**ANSWER:**
"""

def embed_query(query):
    try:
        response = client.embeddings.create(
            input=query,
            model=EMBED_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error embedding query: {e}")


def get_similar_vectors(query_vector, top_k):
    vectors = index.query(
        namespace='__default__',
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        include_values=True
    )
    return vectors.matches

def get_top_text(vectors):
    top_texts = []
    for v in vectors:
        top_texts.append(v.metadata.get('text'))
    return "\n---\n".join(top_texts)

def generate_response(context, query):
    prompt = prompt_template.format(
        context=context,
        question=query
    )
    response = client.chat.completions.create(
        model=RESPONSE_MODEL,
        messages=[
            { 
                'role': 'user',
                'content': prompt
            }
        ]
    )
    return response.choices[0].message.content

query = input("Ask a question about minecraft: ")
print("Embedding question...")
query_vector = embed_query(query)
print("Finding possible articles...")
results = get_similar_vectors(query_vector, 5)
print("Generating your answer, please wait...\n")
context = get_top_text(results)
response = generate_response(context, query)
print(response)
