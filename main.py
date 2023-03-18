import os
from fastapi import FastAPI
import requests
import json
from pydantic import BaseModel
import base64


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PHONE_GPT_KEY = os.getenv('PHONE_GPT_KEY')


class ChatRequest(BaseModel):
    text: str
    history: str = base64.b64encode(
        bytes('[]', 'utf-8')
    )
    key: str

app = FastAPI()


@app.post("/chat")
def chat(chat: ChatRequest):
    text = chat.text
    history = json.loads(
        base64.b64decode(
            chat.history
        ).decode('utf-8')
    )
    key = chat.key
    if key != PHONE_GPT_KEY:
        return 'Unauthorized'
    
    messages = history + [
        {
            'role': 'user',
            'content': text,
        },
    ]
    
    request = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            'model': 'gpt-3.5-turbo',
            'messages': messages,
        },
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}',
        },
    )

    response = json.loads(request.content)

    message = response['choices'][0]['message']['content'].strip()
    history = history + [
        {
            'role': 'user',
            'content': text,
        },
        {
            'role': 'assistant',
            'content': message,
        },
    ]

    return {
        'message': message,
        'history': base64.b64encode(
            bytes(
                json.dumps(history),
                'utf-8',
            )
        ),
    }
