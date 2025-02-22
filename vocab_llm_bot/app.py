from string import Template
from typing import TypedDict

from openai import OpenAI

from enum import Enum

from vocab_llm_bot.config import Config
from vocab_llm_bot.dict_file import DictFile

START_PROMPT = Template("""You is translate assistant.
Below is the pair - word in $lang_from and translation in $lang_to.

$lang_from: $world_from
$lang_to: $world_to

Ask user - how the word is translated from $lang_to to $lang_from?
""")

QUESTION_TEMPLATE = Template("""How is the word "$world_to" translated from $lang_to to $lang_from?""")


class RoleMessage(str, Enum):
    system = 'system'
    assistant = 'assistant'
    user = 'user'


class Message(TypedDict):
    role: RoleMessage
    content: str


class UserDialogCtx:
    def __init__(self, dict_file: DictFile):
        self.config = Config()
        self.client = OpenAI(api_key=self.config.openai_api_key)
        self.dict_file = dict_file
        self._messages_ctx: list[Message] = []
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
                lang_from=lang_from,
                lang_to=lang_to,
                world_from=self._current_words[0],
                world_to=self._current_words[1]
            )}
        ]
        assistant = QUESTION_TEMPLATE.substitute(
            lang_from=lang_from,
            lang_to=lang_to,
            world_from=self._current_words[0],
            world_to=self._current_words[1]
        )
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

        assistant = self.get_completion(self._messages_ctx)
        self._messages_ctx.append({"role": "assistant", "content": assistant})
        return assistant
