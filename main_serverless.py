import os
import requests
import json
import base64


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PHONE_GPT_KEY = os.getenv('PHONE_GPT_KEY')

def chat(request):
    params = request.get_json(silent=True)
    key = params['key']
    if key != PHONE_GPT_KEY:
        return 'Unauthorized'
    text = params['text']
    history = params.get('history') or 'W10='

    history = json.loads(
        base64.b64decode(
            history
        ).decode('utf-8')
    )
    
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
        ).decode('utf-8'),
    }
