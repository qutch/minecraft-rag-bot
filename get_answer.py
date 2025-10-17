import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

# Set up FastAPI
app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'example message'}



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
3.  **If the CONTEXT does not contain the information** needed to answer the QUESTION, you must respond with: "I'm sorry, but I do not have the answer. Please check out the following articles:"
4.  **Be direct and concise.** Get straight to the point and avoid unnecessary fluff.
5.  **Use a friendly and helpful tone,** as if you were another Minecraft player.
6.  **Use markdown formatting** (like bullet points, numbered lists, or bolding key terms) to improve readability, especially for crafting recipes, steps, or lists of items.
7.  **Your primary context is Java Edition Survival Mode. Filter all information to ensure it is only relevant to this context. Do not mention Bedrock Edition, Creative Mode, or other variants unless the user's question explicitly asks about them.
8.  **You must provide all document_urls from the metadata at the end of each message. Do not offer any other resources except for these links such as metadata titles.

---

**CONTEXT:**
{context}

---

**QUESTION:**
{question}

---

**ANSWER:**
"""

def embed_query(query: str) -> list[float]:
    """
    Takes a user's query and embeds it into a 1536 dimension vector
    """
    try:
        embed_response = client.embeddings.create(
            input=query,
            model=EMBED_MODEL
        )
        return embed_response.data[0].embedding
    except Exception as e:
        print(f"Error embedding query: {e}")


def get_similar_vectors(query_vector: list[float], top_k: int) -> list[list[float]]:
    """ 
    Takes a user's query vector and gets the 
    k most similar vectors from the database 
    """
    vectors = index.query(
        namespace='recipe-data',
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        include_values=True
    )
    return vectors.matches

def get_top_text(vectors: list[list[float]], k: int) -> str:
    """
    Gets the top k text's and from the vectors
    Returns a single string with each text inside it
    """
    top_texts = []
    for i in range(k):
        top_texts.append(vectors[i].metadata.get('text'))
        top_texts.append(vectors[i].metadata.get('recipe'))
        top_texts.append('link: ' + vectors[i].metadata.get('document_url'))
    return "\n---\n".join(top_texts)

def generate_response(context: str, query: str) -> str:
    """
    Generates a response from a given context and user query
    """
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

def ask_user_question():
    query = input("ask a question about minecraft: ")
    return query

def get_user_answer(query):
    print("Embedding question...")
    query_vector = embed_query(query)
    print("Finding possible articles...")
    results = get_similar_vectors(query_vector, 10)
    print("Generating your answer, please wait...\n")
    context = get_top_text(results, 10)
    response = generate_response(context, query)
    return response

q = ask_user_question()
a = get_user_answer(q)
print(a)
