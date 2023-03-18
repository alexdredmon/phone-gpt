import base64
from fastapi import FastAPI
import json
import os
from pydantic import BaseModel
import re
import requests


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PHONE_GPT_KEY = os.getenv('PHONE_GPT_KEY')


class ChatRequest(BaseModel):
    text: str
    history: str = base64.b64encode(
        bytes('[]', 'utf-8')
    )
    key: str
    phone: bool = False

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
    phone = chat.phone
    if key != PHONE_GPT_KEY:
        return 'Unauthorized'
    
    messages = history + [
        {
            'role': 'user',
            'content': text,
        },
    ]
    
    params = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
    }
    if phone:
        params['max_tokens'] = 125
    request = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json=params,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}',
        },
    )

    response = json.loads(request.content)

    message = response['choices'][0]['message']['content'].strip()
    if phone:
        trunc_match = re.match(r'(.*)[\.!\?]', message)
        message = trunc_match[0]
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
