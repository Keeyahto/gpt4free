import os
import time
import json
import random
from g4f.Provider import (
    Ails,
    You,
    Bing,
    Yqcloud,
    Theb,
    Aichat,
    Bard,
    Vercel,
    Forefront,
    Lockchat,
    Liaobots,
    H2o,
    ChatgptLogin,
    DeepAi,
    GetGpt,
    Aws,
    Ora,
    Phind,
    Pierangelo
)
from g4f import Model, ChatCompletion, Provider
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

providers = [
    #Ails,
    #You,
    Bing,
    #Yqcloud,
    #Theb,
    Aichat,
    Bard,
    Vercel,
    Forefront,
    Lockchat,
    Liaobots,
    H2o,
    ChatgptLogin,
    DeepAi,
    GetGpt,
    Aws,
    Ora,
    Phind,
    Pierangelo
]


def get_working_provider(model, streaming):
    for provider in providers:
        try:
            ChatCompletion.create(model=model, stream=streaming, messages=[
                                     {"role": "user", "content": "Привет!"}], provider=provider)
            return provider
        except Exception:
            continue

    # Если все провайдеры не работают, можно выбрать дефолтный провайдер
    # или выполнять дополнительные действия, например, отправить уведомление администратору
    # В данном примере, если нет работающего провайдера, вернем None
    return None


provider = Bing
model_name = 'gpt-4'

@app.route("/chat/completions", methods=['POST'])
def chat_completions():
    global provider
    streaming = request.json.get('stream', False)
    print(request.json)
    model = request.json.get('model', model_name)
    messages = request.json.get('messages')
    try:
        response = ChatCompletion.create(model=model, stream=streaming, messages=messages, provider=provider)
    except:
        provider = get_working_provider(model_name, request.json.get('stream', False))
        if provider is None:
            # Если нет работающего провайдера, возвращаем ошибку
            raise Exception('No working provider available')
        response = ChatCompletion.create(model=model, stream=streaming, messages=messages, provider=provider)
    if not streaming:
        while 'curl_cffi.requests.errors.RequestsError' in response:
            try:
                response = ChatCompletion.create(model=model, stream=streaming, messages=messages, provider=provider)
            except:
                provider = get_working_provider(model_name, request.json.get('stream', False))
                if provider is None:
                    # Если нет работающего провайдера, возвращаем ошибку
                    raise Exception('No working provider available')
                response = ChatCompletion.create(model=model, stream=streaming, messages=messages, provider=provider)

        completion_timestamp = int(time.time())
        completion_id = ''.join(random.choices(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))

        return {
            'id': 'chatcmpl-%s' % completion_id,
            'object': 'chat.completion',
            'created': completion_timestamp,
            'model': model,
            'usage': {
                'prompt_tokens': None,
                'completion_tokens': None,
                'total_tokens': None
            },
            'choices': [{
                'message': {
                    'role': 'assistant',
                    'content': response
                },
                'finish_reason': 'stop',
                'index': 0
            }]
        }

    def stream():
        for token in response:
            completion_timestamp = int(time.time())
            completion_id = ''.join(random.choices(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=28))

            completion_data = {
                'id': f'chatcmpl-{completion_id}',
                'object': 'chat.completion.chunk',
                'created': completion_timestamp,
                'model': 'gpt-3.5-turbo-0301',
                'choices': [
                    {
                        'delta': {
                            'content': token
                        },
                        'index': 0,
                        'finish_reason': None
                    }
                ]
            }

            yield 'data: %s\n\n' % json.dumps(completion_data, separators=(',' ':'))
            time.sleep(0.1)

    return app.response_class(stream(), mimetype='text/event-stream')


if __name__ == '__main__':
    config = {
        'host': '0.0.0.0',
        'port': 1337,
        'debug': True
    }

    app.run(**config)
