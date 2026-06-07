import urllib.request, json, os

token = os.environ.get('HF_API_TOKEN', '')
model = 'BrianGithinji/mama-flan-t5'

# Try standard inference endpoint
url = f'https://api-inference.huggingface.co/models/{model}'

payload = json.dumps({
    'inputs': 'maternal health conversation:\nPatient: I have a headache\nMAMA:',
    'parameters': {'max_new_tokens': 150, 'temperature': 0.7, 'do_sample': True, 'return_full_text': False},
    'options': {'wait_for_model': True, 'use_cache': False}
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        result = r.read().decode()
        print('STATUS:', r.status)
        print('RESPONSE:', result)
except urllib.error.HTTPError as e:
    print('HTTP ERROR:', e.code, e.read().decode())
except Exception as e:
    print('ERROR:', type(e).__name__, str(e))
