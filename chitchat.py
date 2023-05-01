from tools import GptContact
import textwrap

bot1 = GptContact()
bot1.set_system_message("### Kontekst : \n Jesteś czterolatkiem ciekawym świata."
                        "### Styl wypowiedzi \n : Krótkie, nieskładne wypowiedzi.")
bot2 = GptContact()
bot2.set_system_message("### Kontekst : \n Jesteś filzofem.."
                        "### Styl wypowiedzi \n : Krótkie, przemyślane odpowiedzi.")

greeting = "Witaj!"
bot1.add_user_message(greeting)
print(greeting)

while True:
    answer = bot1.get_completion(max_tokens=300)
    print(textwrap.fill(f'Dziecko : {answer}', width=110), "\n")
    bot2.add_user_message(answer)
    answer2 = bot2.get_completion(max_tokens=300)
    print(textwrap.fill(f'Filozof : {answer2}', width=110), "\n")
    bot1.add_user_message(answer2)
    ending = GptContact.get_chat_completion(
        "Czy wypowiedź zawiera pożegnanie? Odpowiadaj tylko TAK lub NIE", answer + " " + answer2)
    if "TAK" in ending:
        break
