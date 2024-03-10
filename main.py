import json
import time
import requests
from utils import load_config, write_tokens

CHAT_ID = load_config()['chat_id']
CHAT_URL = f'https://kimi.moonshot.cn/api/chat/{CHAT_ID}/completion/stream'
REFRESH_INTERVAL = 5 * 60
REFRESH_URL = 'https://kimi.moonshot.cn/api/auth/token/refresh'
LIST_URL = 'https://kimi.moonshot.cn/api/chat/list'
NEW_CHAT_URL = 'https://kimi.moonshot.cn/api/chat'

HEADERS = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Content-Type': 'application/json',
    'Referer': 'https://kimi.moonshot.cn',
    'Origin': 'https://kimi.moonshot.cn',
}


# list 和 create 头部都是 auth_token 来鉴权
def list_conversations():
    response = requests.post(LIST_URL, headers=HEADERS, json={}).json()
    return response['items']


def create_conversation(name):
    response = requests.post(NEW_CHAT_URL,
                             headers=HEADERS,
                             json={'name': name}).json()
    return response['id']


async def get_reply(messages):
    HEADERS['Authorization'] = load_config()['auth_token']
    # chat_id = create_conversation('新的聊天')
    # 添加文件，需要在 Kimi 官方上传好
    # messages.append({'content': 'https://prod-chat-kimi.tos-s3-cn-beijing.volces.com/prod-chat-kimi/ckiuir33aesg978thq90/2024-03-03/cnhtnlsudu6ec6vquo9g/3e4545519d5a8a56256980d9fda4f2de_720w_thumbnail.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKLTYTJlNjgwMjY2ZDBkNDFiYmI5YWNiZDBlZmFmYjIzZTA%2F20240303%2Fcn-beijing%2Fs3%2Faws4_request&X-Amz-Date=20240303T020928Z&X-Amz-Expires=518400&X-Amz-SignedHeaders=host&X-Amz-Signature=f9c5dc63e55256871a54f453bc23efde8a9a78078cd7e778cf4dad86987e0a4b', 'type': 'file'})
    response = requests.post(CHAT_URL,
                             headers=HEADERS,
                             json={'messages': [messages[-1]], 'history': messages[:-1]})
    status_code = response.status_code
    if status_code != 200:
        print(status_code)
        print(response.content.decode('utf-8'))
    else:
        for r in response.iter_lines():
            if r:
                decoded = r.decode('utf-8')
                if decoded.startswith('data:'):
                    json_data = json.loads(decoded[len('data: '):])
                    if json_data['event'] == 'cmpl':
                        answer = json_data['text']
                        yield json.dumps(
                            {
                                "object": "chat.completion.chunk",
                                "model": "moonshot-v1",
                                "choices": [
                                    {
                                        "delta":  {"content": answer},
                                        "index": 0,
                                        "finish_reason": None,
                                    }
                                ],
                            }
                        )
    yield json.dumps(
        {
            "object": "chat.completion.chunk",
            "model": "moonshot-v1",
            "choices": [
                {
                    "delta":  {},
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
        }
    )


def refresh():
    global refresh_token
    refresh_token = load_config()['refresh_token']
    HEADERS['Authorization'] = refresh_token
    response = requests.get(REFRESH_URL, headers=HEADERS).json()
    auth_token, refresh_token = list(response.values())
    refresh_token = f'Bearer {refresh_token}'
    auth_token = f'Bearer {auth_token}'
    write_tokens(auth_token, refresh_token)


if __name__ == '__main__':
    while True:
        refresh()
        print('Refresh......')
        time.sleep(REFRESH_INTERVAL)
