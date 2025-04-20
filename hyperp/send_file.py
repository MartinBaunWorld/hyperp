import requests

def send_file(url: str, source: str) -> dict:
    try:
        with open(source, 'rb') as f:
            files = {'file': (source, f)}
            response = requests.post(url, files=files)
            response.raise_for_status()
            return {"msg": "ok", "response": response}
    except Exception as e:
        return {"msg": str(e)}
