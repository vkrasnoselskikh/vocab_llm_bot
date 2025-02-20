from string import Template
from openai import OpenAI
from colorama import Fore, Style

from vocab_llm_bot.config import Config
from vocab_llm_bot.dict_file import DictFile

START_PROMPT = Template("""   
You is translate assistant.
Below is the pair - word in $lang_from and translation in $lang_to.

$lang_from: $eng_world
$lang_to: $rus_world

Ask  user how the word is translated from $lang_to to $lang_from. 
""")


class UserDialogCtx:
    def __init__(self, dict_file: DictFile):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.dict_file = dict_file
        self._messages_ctx: list[dict] = []
        self._current_words: tuple[str, str] | None = None

    def get_completion(self, messages) -> str:
        resp = self.client.chat.completions.create(model='gpt-4o-mini', messages=messages)
        assistant_resp = resp.choices[0].message.content
        return assistant_resp

    def next_word(self) -> str:
        """ Return assistant message"""
        self._current_words = self.dict_file.get_random_word()
        lang_from, lang_to = self.dict_file.get_language_params()

        self._messages_ctx = [
            {"role": "system", "content": START_PROMPT.substitute(
                lang_from=lang_from, lang_to=lang_to,
                eng_world=self._current_words[0],
                rus_world=self._current_words[1]
            )}
        ]
        assistant = self.get_completion(self._messages_ctx)
        self._messages_ctx.append({"role": "assistant", "content": assistant})
        return assistant

    def analyze_user_input(self, user_input: str):
        if user_input in ['I dont know', '--']:
            return self._current_words[0]

        self._messages_ctx.append({"role": "user", "content": user_input})
        self._messages_ctx.append({
            "role": "system",
            "content": 'If I answered correctly, write "correct" else "incorrect" and show translate'
        })

        result = self.get_completion(self._messages_ctx)
        print(Fore.LIGHTMAGENTA_EX + self.get_completion(ctx) + Fore.GREEN + Style.BRIGHT)
        return result

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
