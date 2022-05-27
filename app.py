import configparser
import csv
import random
from configparser import SafeConfigParser
from time import sleep

import pandas as pd
import xlsxwriter
from telethon import TelegramClient
from telethon import errors
from telethon import functions, types
from telethon.tl.functions.messages import AddChatUserRequest


class App:
    __api_id: int = 0
    __ip_group: int = 0
    __api_hash = ""
    __app_name = ""
    __client = None
    __sec = 10

    def __init__(self, config_path: str = "config.ini", path_to_csv: str = "contacts.csv"):
        self.path_to_csv = path_to_csv
        self.config_path = config_path

    def __init_config(self):
        config = SafeConfigParser()
        if not config.read(self.config_path):
            print("Путь к конфигу не найден")
            sleep(self.__sec)
            raise SystemExit
        try:
            self.__id_group = int(config.get("DEFAULT", "ID_GROUP"))
            self.__api_id = int(config.get("DEFAULT", "API_ID"))
            self.__api_hash = config.get("DEFAULT", "API_HASH")
            self.__app_name = config.get("DEFAULT", "CLIENT_NAME")
        except configparser.NoOptionError:
            print("Ошибка имен в конфиге")
            sleep(self.__sec)
            raise SystemExit

    def __create_client(self):
        self.__init_config()
        try:
            self.__client = TelegramClient(self.__app_name, self.__api_id, self.__api_hash)
        except ValueError:
            print("Неверно указаны данные для авторизации клиента")
            sleep(self.__sec)
            raise SystemExit

    def __output_excel(self, names, phones, error):
        name = "output.xlsx"
        df = pd.DataFrame({"Имя": names, "Телефон": phones, "Ошибка": error})
        try:
            df.to_excel(name, index=False)
        except xlsxwriter.exceptions.FileCreateError:
            print(f"Закройте файл с именем: {name}")
            sleep(self.__sec)
            raise SystemExit

    async def __added_users(self):
        names = []
        phones = []
        error = []
        await self.__client.connect()
        try:
            with open(self.path_to_csv, encoding="utf-8") as contacts:
                csv_reader = csv.reader(contacts)
                for line in csv_reader:
                    if line[0] == "Name":
                        continue
                    if len(line[0].split()) > 1:
                        name, surname, *_ = line[0].split()
                    else:
                        name = line[0]
                        surname = ""
                    phone = line[30].replace(" ", "").replace("-", "")
                    names.append(line[0])
                    phones.append(phone)
                    user = await self.__client(functions.contacts.ImportContactsRequest(
                        contacts=[types.InputPhoneContact(
                            client_id=random.randrange(-2 ** 63, 2 ** 63),
                            phone=phone,
                            first_name=name,
                            last_name=surname
                        )]
                    ))
                    try:
                        user_id = user.to_dict()['imported'][0]["user_id"]
                        await self.__client(AddChatUserRequest(user_id=user_id, fwd_limit=0, chat_id=self.__id_group))
                        error.append("Добавлен")
                    except IndexError:
                        error.append("Проблема с данными")
                    except errors.rpcerrorlist.UserAlreadyParticipantError:
                        error.append("Уже добавлен")
        except FileNotFoundError:
            print("Не найден файл с таблицей")
            sleep(self.__sec)
            raise SystemExit
        self.__output_excel(names, phones, error)
        print("Готово")
        sleep(self.__sec)

    def start(self):
        self.__create_client()
        with self.__client:
            self.__client.loop.run_until_complete(self.__added_users())
