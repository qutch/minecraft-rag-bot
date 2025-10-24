from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from get_answer import get_user_answer

app = FastAPI()

origins = [
    'http://localhost:5173/',
    'localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/ask')
async def get_answer(q: str):
    answer = await get_user_answer(query=q)
    return {'response' : answer }
