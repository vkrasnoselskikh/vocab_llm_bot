import io
import logging
from random import choice

import httpx
import pandas as pd
from vocab_llm_bot.config import Config

logger = logging.getLogger(__name__)

class DictFile:
    def __init__(self):
        google_sheet_link = Config().google_sheet_link
        resp = httpx.get(google_sheet_link)
        io_content = io.StringIO(resp.text)
        io_content.seek(0)
        self.df = pd.read_html(io_content, header=1)[0]
        logger.info(f'Downloaded dict: {self.df.shape[0]} rows')

    def get_language_params(self) -> tuple[str, str]:
        return 'English', 'Russian' # Todo  - get language params from file

    def get_random_word(self) -> tuple[str, str]:
        idx = choice(range(self.df.shape[0]))
        eng_word = self.df.iloc[idx]['English']
        rus_word = self.df.iloc[idx]['Russian']
        return eng_word, rus_word
