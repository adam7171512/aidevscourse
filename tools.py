import json
import requests
import openai
from typing import Dict, List
from enum import Enum
import configparser
import tiktoken

config = configparser.ConfigParser()
config.read("config.ini")

AI_DEVS_TASK_TOKEN_URL = "https://zadania.aidevs.pl/token/"
AI_DEVS_TASKS_URL = "https://zadania.aidevs.pl/task/"
AI_DEVS_ANSWERS_URL = "https://zadania.aidevs.pl/answer/"
AI_DEVS_KEY = config.get("api", "AI_DEVS_KEY")
OPEN_AI_MODERATION_URL = "https://api.openai.com/v1/moderations"
openai.api_key = config.get("api", "OPEN_AI_KEY")

token_limits = {
    "gpt-3.5-turbo": 4096
}


def str_token_count(s: str) -> int:
    return len(tiktoken.get_encoding("cl100k_base").encode(s))


class Role(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class TaskManager:

    def __init__(self, task_name: str):
        self.task_name = task_name
        self._task_token = None
        self._task = None

    @property
    def task_token(self) -> str:
        if not self._task_token:
            self._task_token = self._obtain_task_token()
        return self._task_token

    @property
    def task(self) -> Dict[str, any]:
        if not self._task:
            self._task = self._obtain_task()
        return self._task

    def solve(self, func: callable):
        if self._submit_solution(func(self.task)):
            print(f'Congratulations! Task {self.task_name} solved.')
        else:
            raise RuntimeError("Something went wrong..")

    def _obtain_task_token(self) -> str:
        data = {"apikey": AI_DEVS_KEY}
        url = f"{AI_DEVS_TASK_TOKEN_URL}{self.task_name}"
        response = requests.post(url, json=data).json()
        self.check_response(response)
        return response.get("token")

    def _obtain_task(self) -> Dict[str, any]:
        response = requests.get(f"{AI_DEVS_TASKS_URL}{self.task_token}").json()
        self.check_response(response)
        return response

    def _submit_solution(self, answer: any) -> bool:
        answer_to_send = {'answer': answer}
        response = requests.post(f"{AI_DEVS_ANSWERS_URL}{self.task_token}", json=answer_to_send).json()
        return self.check_response(response)

    @staticmethod
    def check_response(response: Dict[str, any]) -> bool:
        code = response.get("code")
        if code:
            raise ValueError(f'{response}')
        return True


class GptContact:

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self._system_message = {"role": "system", "content": ""}
        self.conversation = []
        self.model = model
        self.model_token_limit = token_limits.get(self.model, "2048")

    @property
    def system_message(self) -> str:
        return self._system_message.get("content")

    @system_message.setter
    def system_message(self, message: str):
        self._system_message["content"] = message

    def set_system_message(self, message: str):
        self.system_message = message
        return self

    def add_user_message(self, message: str):
        self.conversation.append({"role": "user", "content": message})
        return self

    def add_message(self, message: str, role: Role):
        self.conversation.append({"role": role.value, "content": message})
        return self

    def get_completion(self,
                       temperature: float = 1,
                       max_response_tokens=1000,
                       chat_history_token_limit=None,
                       chat_history_recent_messages_limit=None):

        if not self.conversation:
            raise ValueError("No messages to send!")

        messages = []

        sys_message_tokens = str_token_count(str(self._system_message)) if self.system_message else 0
        chat_history_tokens_available = self.model_token_limit - sys_message_tokens - max_response_tokens

        if chat_history_token_limit:
            chat_history_tokens_available = min(chat_history_token_limit, chat_history_tokens_available)

        messages_appended = 0
        for message in reversed(self.conversation):
            message_token_count = str_token_count(str(message))
            if chat_history_recent_messages_limit and messages_appended >= chat_history_recent_messages_limit:
                break
            elif chat_history_tokens_available < message_token_count:
                break
            messages.insert(0, message)
            chat_history_tokens_available -= message_token_count
            messages_appended += 1

        if self.system_message:
            messages.insert(0, self._system_message)

        answer = GptContact.get_chat_completion_for_formatted_input(
            messages, self.model, temperature, max_response_tokens)
        self.conversation.append({"role": "assistant", "content": answer})
        return answer

    @staticmethod
    def get_moderation_info(content: str):
        response = requests.post(
            OPEN_AI_MODERATION_URL,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + openai.api_key},
            data=json.dumps({"input": content})
        )
        return response.json()

    @staticmethod
    def get_chat_completion_for_formatted_input(messages: List[Dict],
                                                model: str = "gpt-3.5-turbo",
                                                temperature: float = 1,
                                                max_tokens=1999):
        response = openai.ChatCompletion.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens)
        return response.choices[0].message.content

    @staticmethod
    def get_chat_completion(system_message: str,
                            user_message: str,
                            model: str = "gpt-3.5-turbo",
                            temperature: float = 1,
                            max_tokens=1999):
        inp = ApiInputBuilder().add_message(Role.SYSTEM, system_message) \
            .add_message(Role.USER, user_message).build()
        return GptContact.get_chat_completion_for_formatted_input(
            inp, model, temperature, max_tokens)


class ApiInputBuilder:
    def __init__(self):
        self.messages = []

    def add_message(self, role: Role, content: str):
        self.messages.append(
            {"role": role.value, "content": content}
        )
        return self

    def build(self):
        return self.messages
