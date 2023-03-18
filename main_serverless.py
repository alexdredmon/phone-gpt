import base64
import json
import re
import requests


def chat(request):
    params = request.get_json(silent=True)
    key = params.get('key')
    if key != '':
        return 'Unauthorized'
    text = params['text']
    history = params.get('history') or 'W10='
    phone = params.get('phone') or False
    max_tokens = params.get('max_tokens') or 125
    raw = params.get('raw') or False
    if not raw:
        text = text + " Please keep your response brief."

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
    
    params = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
    }
    if phone:
        params['max_tokens'] = max_tokens
    request = requests.post(
        'https://api.openai.com/v1/chat/completions',
        json=params,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer ',
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
        ).decode('utf-8'),
    }
