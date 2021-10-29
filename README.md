# kaspersky-test-task

> Заголовки на английском и без пробелов для того, чтобы можно было использовать ссылки на них
## Содержание:

* [Setup](#Setup)
* [Using](#Using)
* [Testing and developing](#Testing_and_developing)
* [P.s.](#P.s.)


---
# Setup

Есть два способа: обычный из через докер.
В основном проект затачивался под доцкер, так что с него и начнем

## Docker


### Зависимости:
* Docker, Docker-compose

### Процесс:

Запуск следующей команды в терминале в root директории
```bash
docker-compose up
```

Тесты запускаются при сборке образа, и, если они не проходят - cборка образа завершается с ошибкой!

---
## Обычный:

### Зависимости:
* Python >= 3.8
* pip
* MongoDB instance
* RabbitMQ instance

### Процесс:
* Создание виртуального окружения, его активация и установка всех зависимостей:
```bash
python3 -m venv kaspersky_env
source ./kaspersky_env/bin/activate
pip install -r requirements.txt
```
* Экспорт необходимых переменных окружения (в целом, можете изменить их по желанию):
```bash
export MONGO_URI=<uri вашего инстанса mongodb>
export AMQP_URI=<uri вашего инстанса rabbitmq>

export MONGO_DBNAME=dev
export MONGO_COLLECTION=tasks
export QUEUE_NAME=Tasks
export HOST=localhost
```
* Запуск тестов:
```bash
pytest
```
* Запуск самого проекта:
```bash
python ./main.py
```
<br></br>


---
# Using

Взаимодействие происходит через RestAPI, так что можно использовать как [веб-страницу](http://localhost:8000/tasks), так и средства для отправки запросов (`curl`, `Postman`, `requests`, `httpx`, `fetch`, `axios`, etc).

* `/tasks` - относительный адрес для отправки POST-запроса с любыми данными в теле запроса, например:
<details>
  <summary>Пример объекта <code>json</code></summary>

  ```json
  {
    "someKey": "someData",
    "anotherKey": 543.7876,
    "lastOne": {
      "nestedKey": "nestedValue",
      "nestedKey2": "nestedValue2"
    }
  }
  ```
</details>

<details>
  <summary>Скриншот</summary>

  ![Form](/assets/screenshot_form_containg_json.png)
</details>

<br></br>

* Далее мы нажимаем на кнопку Create, и через чуть более 2 секунды получаем `alert` с сообщением "task {{ Наш таск }} is queued"

<details>
  <summary>Скриншот</summary>

  ![Alert first](/assets/screenshot_alert_first.png)
</details>

<br></br>

* В течение около последующих 10 секунд мы можем пытаться отправить эти же данные, но мы будем получать лишь сообщение с уже существующей записью и полем `status` со значением "Waiting"


<details>
  <summary>Скриншот</summary>

  ![Waiting](/assets/screenshot_waiting.png)
</details>

<br></br>

* А после - "Done"

<details>
  <summary>Скриншот</summary>

  ![Done](/assets/screenshot_done.png)
</details>

<br></br>

---
# Testing_and_developing

Тесты написаны с использованиям моков для объектов, использующих сторонние службы напрямую, вроде MongoDB и RabbitMQ (паттерн [Humble Object](http://xunitpatterns.com/Humble%20Object.html))

Для тестирования можно просто заменить эти моки на объекты, которые используются по умолчанию (если, конечно, службы, с которыми они взаимодействуют, в данный момент доступны для обращения к ним).

Для взаимодействия со средством хранения данных (базой данных, файловой системой, т.д.) можно просто реализовать наследника абстрактного класса `store.BaseStore`, создать его экземпляр и инъецировать этот экземпляр при вызове функции `main.create_app`  

---
# P.s.
Не стал разбираться с `logging`, `loguru` и т.д., а реализовал через `print`.
Не стал разбираться с изяществом веб-страницы.

Не то, чтобы было бы сложно, но, уверен, идея ТЗ состояла не в этом
