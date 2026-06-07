import urllib.request, json

for path in ['/health', '/debug/ai']:
    try:
        r = urllib.request.urlopen(f'http://localhost:8000{path}', timeout=10)
        data = json.loads(r.read().decode())
        print(f"\n=== {path} ===")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"\n=== {path} ERROR ===")
        print(e)
