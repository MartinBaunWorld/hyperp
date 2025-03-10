import json
import requests


def _format_json_value(value):
    """Format JSON values to be compatible with HTTPie syntax."""
    if isinstance(value, dict):
        return f":='{json.dumps(value)}'"
    elif isinstance(value, list):
        return f":='{json.dumps(value)}'"
    elif isinstance(value, bool):
        return ':=true' if value else ':=false'
    elif isinstance(value, (int, float)):
        return f":={value}"
    elif value is None:
        return 'null'
    else:
        return f'"{value}"'


def httpie(response, *args, **kwargs):
    method = response.request.method
    url = response.request.url
    headers = response.request.headers
    data = response.request.body
    
    httpie_cmd = f"http {method.lower()} {url} \\\n"
    
    if headers:
        for k, v in headers.items():
            httpie_cmd += f"    '{k}: {v}' \\\n"
    
    if data:
        content_type = headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON data
            json_data = json.loads(data)
            data_pairs = [f"{k}={_format_json_value(v)}" if isinstance(v, str) else f"{k}{_format_json_value(v)}" for k, v in json_data.items()]
            httpie_cmd += f"    {' '.join(data_pairs)}"
        elif 'application/x-www-form-urlencoded' in content_type:
            # Form data
            data_pairs = [f"{k}={v}" for k, v in [pair.split('=') for pair in data.split('&')]]
            httpie_cmd += f"    {' '.join(data_pairs)}"
        else:
            # Other types of data (raw body, etc.)
            # TODO this have not yet been tested
            httpie_cmd += f"    {data}"
    
    print(httpie_cmd.strip())
    print('')
    print(data)
    print('\n\n')
    print('' + '-' * 40)
    print('\n\n')
