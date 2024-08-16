import requests


class Play:
    """
        Thin wrapper that hels you play with an API
        while at the same time make documentation for it
        in form of httpie/bash scripts
        Experimental and will not be backward compatible
    """
    def __init__(self, url):
        self.url = url

    def post(self, path, json, auth=None):
        headers = {}
        args = []

        if auth:
            headers['authorization'] = auth
            args.append(f'"authorization: {auth}"')

        r = requests.post(
            f'{self.url}{path}',
            json=json,
            headers=headers,
        ).json()

        for k, v in json.items():
            args.append(f'{k}={v}')

        print(f'http POST {self.url}{path} \\')
        print('\t' + ' \\\n\t'.join(args))
        print('')
        print(r)
        print('')
        print('')
        print('#' + '-' * 10)
        return r
