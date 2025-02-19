from random import choice
import io

import pandas as pd
from string import Template
from openai import OpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict
from colorama import Fore, Back, Style
import httpx


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')
    openai_api_key: str


class DictFile:
    def __init__(self):
        resp = httpx.get(
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFQqWyklZpcjxY0ZA35hYyLntEs7csR-EeyGu3RpvlMoxc_Ucl_LZiSwImJgaerJH5XXvI_VedRQQL/pubhtml")
        cont = io.StringIO(resp.text)
        cont.seek(0)
        self.df = pd.read_html(cont, header=1)[0]
        print(f'Downloaded dict: {self.df.shape[0]} rows')

    def get_random_word(self) -> tuple[str, str]:
        idx = choice(range(self.df.shape[0]))
        eng_word = self.df.iloc[idx]['English']
        rus_word = self.df.iloc[idx]['Russian']
        return eng_word, rus_word


START_PROMPT = Template("""   
You is translate assistant.
Below is the pair - word in English and translation in Russian.

English: $eng_world
Russian: $rus_world

Ask  user how the word is translated from Russian to English. 
""")


class App:
    def __init__(self):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.dict_file = DictFile()

    def get_completion(self, messages) -> str:
        resp = self.client.chat.completions.create(model='gpt-4o-mini', messages=messages)
        assistant_resp = resp.choices[0].message.content
        return assistant_resp

    def main_loop(self):
        while True:
            eng_world, rus_world = self.dict_file.get_random_word()

            ctx = [
                {"role": "system", "content": START_PROMPT.substitute(eng_world=eng_world, rus_world=rus_world)}
            ]
            assistant = self.get_completion(ctx)
            ctx.append({"role": "assistant", "content": assistant})
            print(Fore.LIGHTMAGENTA_EX + assistant + Fore.GREEN + Style.BRIGHT)
            user_input = input()
            if user_input in ['No', '--']:
                print(eng_world)
                continue
            ctx.append({"role": "user", "content": user_input})
            ctx.append({"role": "system",
                        "content": 'If I answered correctly, write "correct" else "incorrect" and show translate'})
            print(Fore.LIGHTMAGENTA_EX + self.get_completion(ctx) + Fore.GREEN + Style.BRIGHT)


def main():
    try:
        app = App()
        app.main_loop()
    except KeyboardInterrupt:
        print(Style.RESET_ALL)
        pass


if __name__ == '__main__':
    main()
