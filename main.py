import base64
from fastapi import FastAPI
import json
import openai
import os
from pydantic import BaseModel
import re
import requests
import time


PHONE_GPT_KEY = os.getenv('PHONE_GPT_KEY')


class ChatRequest(BaseModel):
    text: str
    history: str = base64.b64encode(
        bytes('[]', 'utf-8')
    )
    key: str
    phone: bool = False
    max_execution: int = 4

app = FastAPI()


@app.post("/chat")
def chat(chat: ChatRequest):
    start_x = time.time()
    text = chat.text
    history = json.loads(
        base64.b64decode(
            chat.history
        ).decode('utf-8')
    )
    key = chat.key
    phone = chat.phone
    max_execution = chat.max_execution

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

    streams = []
    message = ""
    for completion in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    ):
        content = completion['choices'][0]['delta'].get('content', '')
        if content:
            message += content
        streams.append(completion)
        elapsed = time.time() - start_x
        if phone and elapsed > max_execution:
            break

    if phone:
        trunc_match = re.search(r'(.*)[\.!\?]', message)
        if trunc_match is not None:
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
        'elapsed': time.time() - start_x,
        'message': message,
        'phone': phone,
        'history': base64.b64encode(
            bytes(
                json.dumps(history),
                'utf-8',
            )
        ).decode('utf-8'),
        'streams': streams,
    }
