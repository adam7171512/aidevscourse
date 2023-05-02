from tools import GptContact
import textwrap

bot1 = GptContact()
bot1.set_system_message(
    "### Kontekst : \n Jesteś Wiedźminem szukającym zleceń. Jeśli ktoś zaproponuje zlecenie, dopytaj"
    "o szczegóły zlecenia i wynagrodzenie."
    "### Styl wypowiedzi \n : Krótkie.")
bot2 = GptContact()
bot2.set_system_message("### Kontekst : \n Jesteś wieśniakiem szukającym kogoś kto pomoże ci przegnać strzygę z wioski."
                        "Wyjaśnij rozmówcy istotę problemu."
                        "### Styl wypowiedzi \n : Krótkie wulgarne wypowiedzi, przerażenie.")

greeting = "Witaj!"
bot1.add_user_message(greeting)
print(greeting)


def is_message_a_goodbye(msg: str) -> bool:
    ans = GptContact.get_chat_completion(
        "Czy wiadomość zawiera pożegnanie? Odpowiadaj tylko TAK lub NIE",
        msg, max_tokens=2)
    return "TAK" in ans


def is_conversation_ended(msg1: str, msg2: str) -> bool:
    return is_message_a_goodbye(msg1) and is_message_a_goodbye(msg2)


while True:
    answer = bot1.get_completion(max_response_tokens=200, chat_history_recent_messages_limit=10)
    print(textwrap.fill(f'Wiedźmin : {answer}', width=110), "\n")
    bot2.add_user_message(answer)
    answer2 = bot2.get_completion(max_response_tokens=200, chat_history_recent_messages_limit=10)
    print(textwrap.fill(f'Wieśniak : {answer2}', width=110), "\n")
    bot1.add_user_message(answer2)

    if is_conversation_ended(answer, answer2):
        break
