import requests

def activate_fingerprint():
    response = requests.post(
        'http://localhost:8000/fingerprint/is_active',
        json={'is_active': True}
    )
    return response.json()

def deactivate_fingerprint():
    response = requests.post(
        'http://localhost:8000/fingerprint/is_active',
        json={'is_active': False}
    )
    return response.json()

def set_mode_enroll():
    response = requests.post(
        'http://localhost:8000/fingerprint/mode',
        json={'mode': 'enroll'}
    )
    return response.json()

def set_mode_verify():
    response = requests.post(
        'http://localhost:8000/fingerprint/mode',
        json={'mode': 'verify'}
    )
    return response.json()

def get_current_mode():
    response = requests.get('http://localhost:8000/fingerprint/mode')
    return response.json()