import base64
import json
import openai
import re
import requests
import time

openai.api_key = ''


def chat(request):
    start_x = time.time()
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
    streams = []
    message = ""
    for completion in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        # max_tokens=125,
        stream=True,
    ):
        content = completion['choices'][0]['delta'].get('content', '')
        if content:
            message += content
        streams.append(completion)
        elapsed = time.time() - start_x
        if phone and elapsed > 4:
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
        ).encode('utf-8'),
    }
