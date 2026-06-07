import urllib.request, json

base = "https://briangithinji-mama-lens-ai.hf.space"

# Check debug/network to see token and URL status
for path in ["/debug/network", "/debug/ai"]:
    try:
        r = urllib.request.urlopen(f"{base}{path}", timeout=15)
        print(f"\n=== {path} ===")
        print(json.dumps(json.loads(r.read().decode()), indent=2))
    except Exception as e:
        print(f"\n=== {path} ERROR: {e} ===")
