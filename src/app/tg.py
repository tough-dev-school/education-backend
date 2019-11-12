import requests


def send_happiness_message(text):
    r = requests.post('https://timepad.f213.in/msg/', json={
        'text': text,
    })

    assert r.status_code == 200, 'TG proxy should return 200'
    assert r.json()['ok'] is True, 'TG proxy should say msg is ok'
