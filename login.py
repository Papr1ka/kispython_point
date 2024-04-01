import requests
from bs4 import BeautifulSoup


def login_via_lks(login, password):
    url = "https://kispython.ru/login/lks"
    client = requests.session()

    page = client.get(url, headers={"Referer": "https://kispython.ru/"})  # Referer украден с ручной авторизации

    log_url = page.url  # там куча редиректов после get, поэтому надо не потеряться, где мы сейчас

    parse = BeautifulSoup(page.content, "html.parser")

    csrf_tag = parse.find(name="input", attrs={"name": "csrfmiddlewaretoken"})  # CSRF код
    token = csrf_tag["value"]

    next_tag = parse.find(name="input", attrs={"name": "next"})  # адрес следующего редиректа
    next_url = next_tag["value"]

    data = {
        "csrfmiddlewaretoken": token,
        "login": login,
        "password": password,
        "next": next_url
    }

    client.post(log_url, data=data, headers={"Referer": log_url})

    return client
