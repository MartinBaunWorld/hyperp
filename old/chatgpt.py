from traceback import format_exc

import openai


class ChatGPT:
    def __init__(self, key, on_error=None):
        self.key = key
        self.on_error = on_error

    def generate_message(self, prompt, default=""):
        message = default

        try:
            client = openai.OpenAI(api_key=self.key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", 'content': prompt}],
            )
            message = response.choices[0].message.content.strip()
        except:  # noqa
            self.log_error(format_exc())

        return message

    def log_error(self, data):
        if self.on_error and callable(self.on_error):
            self.on_error(data)


class ChatGPTMock:
    def __init__(self, key):
        self.key = key

    def generate_message(self, prompt, default=""):
        return default
