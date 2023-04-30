from tools import TaskManager, GptContact, ApiInputBuilder, Role
from typing import Dict

"""
Create "config.ini" file and add your API keys :
file content should look like this: 
[api]
AI_DEVS_KEY = 3#@^&#^@&#@^&&#^@&#&^@b
OPEN_AI_KEY = sj3k23283237283729-3#@#@#@v
"""

# lookup task content
task_manager = TaskManager("HelloAPI")
task = task_manager.task
print(task)

# {'code': 0, 'msg': 'please return value of "cookie" field as answer', 'cookie': '***'
# create function taking task as an argument and returning the answer:


def solve_hello_api(api_task: Dict[str, any]) -> str:
    gpt_answer = GptContact(). \
        set_system_message("Return value specified in msg field and nothing more! Omit quotes etc") \
        .add_user_message(str(api_task)) \
        .get_completion()
    print(gpt_answer)
    return gpt_answer


# pass function as an argument to "solve" method in manager
task_manager.solve(solve_hello_api)

# Other ways to use GptContact :

answer = GptContact.get_chat_completion(
    system_message="Answer Yes to every question",
    user_message="Do you like techno?",
    model="gpt-3.5-turbo")
print(answer)

messages = ApiInputBuilder()\
    .add_message(Role.SYSTEM, "Your job is to answer untruthfully. We are just playing jokes.")\
    .add_message(Role.USER, "Is Earth ")\
    .add_message(Role.USER, "flat ?")\
    .build()

answer = GptContact.get_chat_completion_for_formatted_input(messages)
print(answer)

# moderation info
moderation_info = GptContact.get_moderation_info("Moderated input")
print(moderation_info)
flagged = moderation_info.get("results")[0].get("flagged")
print(flagged)
