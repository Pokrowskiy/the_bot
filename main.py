import telebot
import json
import requests as req
from random import randint
from currency_converter import CurrencyConverter

bot = telebot.TeleBot("6901574747:AAE4RkY1LsXzaMDK4feL7jdp73RKq867ECw")
token_geo = "239b4a26e2640edb1c9f1f510b92efe2"
converter = CurrencyConverter()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать!")
    menu_message(message)

@bot.message_handler(commands=["hello"])
def hello_message(message):
    bot.send_message(message.chat.id, "И тебе привет, "+message.from_user.first_name)

menu_text = ("Я могу предложить :\n- Погода в любом городе\n- Генератор случайных чисел\n- Конвертер валют."
             "\n\nИспользуй команду /help, если тебе нужна помощь.\nИ я всегда буду рад, если ты поблагодаришь меня за работу.\nИли просто поздороваешься.")
@bot.message_handler(commands=["menu"])
def menu_message(message):
    bot.send_message(message.chat.id, menu_text)


help_text = """На данный момент бот состоит из следующих функций:\n[Обязательный параметр]<необязательный параметр>
\n\nПогода. Ключевое слово(КС) - "Погода" или "Weather"\nКС [Город]\nПример : Погода Москва\n\n
Рандомайзер. Ключевое слово(КС) - "roll", "куб" или "брось" \n КС <Количество бросков(должно оканчиваться на "d")><Минимум><Максимум>\n Пример : roll 5d10-50\nПри отсутствии параметров выдаёт случаное число (1-100)\n\n
Конвертер валют. Ключевое слово(кс) - "Переведи" или "convert"\n КС [Пара валют] <Сумма перевода>\nПримеры : Переведи EUR/USD   , convert USD/GBP 30\n\n
Также полезные команды : \n \n/start - Начать с начала \n/hello - Вежливо поздороваться с ботом.\n/menu - выход в меню.\n/help - если вы запутались и потерялись."""


@bot.message_handler(commands=["help"])
def help_message(message):
    bot.send_message(message.chat.id, help_text)


def weather(city,message):
    response = req.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token_geo}&units=metric&lang=ru")
    res = json.loads(response.text)
    try:
        temp = "Состояние неба : " + str(res["weather"][0]["description"])
        temp += "\nОблачность : " + str(res["clouds"]["all"]) + "%"
        temp += "\n\nСейчас на улице "+str(res["main"]["temp"])+"C ˚"
        temp += "\nОщущается как  "+str(res["main"]["feels_like"])+"C ˚\n\n"
        tmp = int(res["main"]["temp"])
        ad = ""
        if tmp > 30 :
            ad = "Одевайтесь полегче. На улице жарко!"
        elif tmp > 20 :
            ad = "На улице тепло."
        elif tmp > 10 :
            ad = "Снаружи прохладно, на всякий случай наденьте свитер."
        elif tmp > 0 :
            ad = "Снаружи холодно. Согрейтесь и наденьте куртку."
        elif tmp > -10 :
            ad = "На улице действительно холодно. Тёплая куртка, шарф и шапка вам помогут."
        else:
            ad = "Мне тоже кажется, что выходить туда без скафандра - плохая идея."
        temp += ad
        bot.send_message(message.chat.id, temp)
    except:
        bot.send_message(message.chat.id, "К сожалению, не удалось найти город \""+city+"\" \nПроверьте правильность написания и повторите попытку.")

def clamp(x,a,b):
    if x < a:
        return a
    if x > b:
        return b
    return x

def roll(roll_text,message):
    try:
        if not "d" in roll_text and roll_text.split()[1].isdigit():
            raise FormatError
        count = roll_text.split("d")[0].split(" ")[1]
        if count == "":
            count = 1
        else:
            count = int(count)
        if count < 1 or count > 100:
            count = clamp(count,1,100)
            bot.send_message(message.chat.id, "Количество бросков не входит \nв допустимый диапазон (1-100)\nВведённое количество бросков было приведено \nк ближайшему подходящему числу. ("+str(count)+")")
        try :
            min_n,max_n = roll_text.split("d")[1].split("-")
            min_n,max_n = int(min_n),int(max_n)
            tmp = max(min_n,max_n)
            min_n = min(min_n,max_n)
            max_n = tmp
        except :
            max_n = int(roll_text.split("d")[1])
            min_n = 1
        outp = ""
        sum_n = 0
        for i in range(count):
            rand = randint(min_n,max_n)
            outp += str(rand)+"\n"
            sum_n += rand
        if count != 1:
            outp+= "\navg : "+ str(round(sum_n/count*100)/100)
            outp+= "\ncount = "+str(count)+"\nmax = "+str(max_n)+"\nmin = "+str(min_n)
        bot.send_message(message.chat.id, outp)
    except FormatError:
        r = randint(1, int(roll_text.split()[1]))
        bot.send_message(message.chat.id, str(r))

    except IndexError:
        r = randint(1, 100)
        bot.send_message(message.chat.id,str(r))
    except:
        bot.send_message(message.chat.id, "К сожалению, у меня не \nполучается распознать ввод. \nПопробуйте ещё раз.")

class FormatError(Exception):
    def __init__(self):
        pass

def conv(text,message):
    try:
        text = text.split()[1::]
        if len(text)==0:
            raise FormatError
        curs = text[0]
        if not text[1].isdigit():
            raise FormatError
        amount = float(text[1])
        if amount <= 0:
            raise IndexError
        val1,val2 = curs.upper().split("/")
        res = round(converter.convert(amount, val1,val2),2)
        bot.send_message(message.chat.id,f"{amount} {val1} = {res} {val2}")

    except IndexError:
        try:
            amount = 1
            val1, val2 = curs.upper().split("/")
            res = round(converter.convert(amount, val1, val2),2)
            bot.send_message(message.chat.id,
                             "Не удалось распознать сумму для конвертации.\nВ связи с этим показан стандартный курс.")
            bot.send_message(message.chat.id, f"{amount} {val1} = {res} {val2}")
        except :
            bot.send_message(message.chat.id,
                         "Похоже, произошла ошибка в базе данных...\nЯ не могу найти курс для перевода этих валют.\nПопробуйте позже или другие валюты.")
    except ValueError:
        bot.send_message(message.chat.id,
                         "Похоже, произошла ошибка в базе данных...\nЯ не могу найти курс для перевода этих валют.\nПопробуйте позже или другие валюты.")
    except FormatError:
       bot.send_message(message.chat.id,"Похоже, формат неверен...")

@bot.message_handler()
def info(message):
    text = message.text.lower()
    fst = text.split()[0]

    if fst == "погода":
        try :
            city = text.split()[1]
            weather(city,message)
        except :
            bot.send_message(message.chat.id,"К сожалению, я не смогу найти погоду, \nне зная города, в котором её искать.\n"
                                             "Попробуйте указать название города")

    if fst == "roll" or fst == "куб" or fst == "брось":
        roll(text,message)

    if fst == "переведи" or fst == "convert":
        conv(text,message)

    if "привет" in text:
        bot.send_message(message.chat.id,"Тебе тоже привет, "+message.from_user.first_name)
    if "спасибо" in text or text == "спс" or text == "thx":
        bot.send_message(message.chat.id, "Рад, что вы цените мою работу!")
    if "id чата" in text or "id этого чата" in text:
        bot.send_message(message.chat.id, "С радостью! \n ID : "+str(message.from_user.id))
    elif "id" in text:
        bot.send_message(message.chat.id, "Уточните, пожалуйста, ID чего вы хотите?")

bot.polling(none_stop=True)