import json


def load_config():
    return json.load(open('config.json', encoding='utf-8'))


def write_tokens(auth_token, refresh_token):
    cfg = load_config()
    cfg['auth_token'] = auth_token
    cfg['refresh_token'] = refresh_token
    with open('config.json', 'w', encoding='utf-8') as w:
        w.write(json.dumps(cfg))
