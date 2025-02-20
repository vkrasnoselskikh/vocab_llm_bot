import io
from random import choice

import httpx
import pandas as pd
from vocab_llm_bot.config import Config


class DictFile:
    def __init__(self):
        Config()
        resp = httpx.get(
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vQFQqWyklZpcjxY0ZA35hYyLntEs7csR-EeyGu3RpvlMoxc_Ucl_LZiSwImJgaerJH5XXvI_VedRQQL/pubhtml")
        cont = io.StringIO(resp.text)
        cont.seek(0)
        self.df = pd.read_html(cont, header=1)[0]
        print(f'Downloaded dict: {self.df.shape[0]} rows')

    def get_language_params(self) -> tuple[str, str]:
        return 'English', 'Russian'

    def get_random_word(self) -> tuple[str, str]:
        idx = choice(range(self.df.shape[0]))
        eng_word = self.df.iloc[idx]['English']
        rus_word = self.df.iloc[idx]['Russian']
        return eng_word, rus_word
