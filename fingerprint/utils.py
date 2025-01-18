import requests

def activate_fingerprint():
    response = requests.post(
        'http://localhost:8000/fingerprint/is-active',
        json={'is_active': True}
    )
    return response.json()

def deactivate_fingerprint():
    response = requests.post(
        'http://localhost:8000/fingerprint/is-active',
        json={'is_active': False}
    )
    return response.json()