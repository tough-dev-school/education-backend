import requests


def send_happiness_message(text):
    response = requests.post('https://timepad.f213.in/msg/', json={
        'text': text,
    })

    assert response.status_code == 200, 'TG proxy should return 200'
    assert response.json()['ok'] is True, 'TG proxy should say msg is ok'
