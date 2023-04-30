from ApiInputBuilder import ApiInputBuilder
import requests
import openai
from typing import Dict, List
from enum import Enum
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

AI_DEVS_TASK_TOKEN_URL = "https://zadania.aidevs.pl/token/"
AI_DEVS_TASKS_URL = "https://zadania.aidevs.pl/task/"
AI_DEVS_ANSWERS_URL = "https://zadania.aidevs.pl/answer/"
AI_DEVS_KEY = config.get("api", "AI_DEVS_KEY")
openai.api_key = config.get("api", "OPEN_AI_KEY")


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
        self.system_message = None
        self.user_messages = []
        self.model = model

    def set_system_message(self, message: str):
        self.system_message = message
        return self

    def add_user_message(self, message: str):
        self.user_messages.append(message)
        return self

    def get_completion(self):
        if not self.user_messages:
            raise ValueError("You have to provide User message to get completion!")
        builder = ApiInputBuilder()
        if self.system_message:
            builder.add_message(Role.SYSTEM, self.system_message)
        for user_message in self.user_messages:
            builder.add_message(Role.USER, user_message)
        messages = builder.build()
        return GptContact.get_chat_completion_for_formatted_input(messages, self.model)

    @staticmethod
    def get_chat_completion_for_formatted_input(messages: List[Dict], model: str = "gpt-3.5-turbo"):
        response = openai.ChatCompletion.create(model=model, messages=messages)
        return response.choices[0].message.content

    @staticmethod
    def get_chat_completion(system_message: str, user_message: str, model: str = "gpt-3.5-turbo"):
        inp = ApiInputBuilder().add_message(Role.SYSTEM, system_message) \
            .add_message(Role.USER, user_message).build()
        return GptContact.get_chat_completion_for_formatted_input(inp, model)
