Программа позволяет автоматически добавлять людей из Google контактов в группу Telegram.

Для корректной работы требуется создать файл config.ini и ввести следующие данные:

```
[DEFAULT]

API_ID = 12345

API_HASH = 12345

CLIENT_NAME = test

ID_GROUP = 12345
```


API_ID, API_HASH, CLIENT_NAME - для получения этих полей нужно залогиниться тут https://my.telegram.org/auth

ID_GROUP - id группы, в которую вы хотите добавить людей