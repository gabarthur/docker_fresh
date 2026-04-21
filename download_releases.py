import requests
import os
import time
import re
import getpass
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json

DOWNLOAD_DIR = "distr"
LIST_FILE = "other_files/fresh_components.json"

TIMEOUT = 60
DELAY_BETWEEN_DOWNLOADS = 5

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
})

def login_1c(username: str, password: str) -> bool:
    print("Открываем страницу логина...")

    r = session.get("https://login.1c.ru/login", timeout=TIMEOUT, allow_redirects=True)
    soup = BeautifulSoup(r.text, "html.parser")

    form = soup.find("form")
    if not form:
        print("Форма не найдена.")
        return False

    action = form.get("action")
    if action and action.startswith("/"):
        action = "https://login.1c.ru" + action
    elif not action:
        action = "https://login.1c.ru/login"

    data = {
        "username": username,
        "password": password,
        "_eventId": "submit",
    }

    for inp in form.find_all("input", {"type": "hidden"}):
        name = inp.get("name")
        value = inp.get("value")
        if name:
            data[name] = value

    print("Отправляем форму на", action)
    r = session.post(action, data=data, timeout=TIMEOUT, allow_redirects=True)

    print("Статус:", r.status_code, "| URL:", r.url)

    if "/user/profile" in r.url:
        print("Попали в личный кабинет. Переходим на releases.1c.ru...")
        r = session.get("https://releases.1c.ru/", timeout=TIMEOUT, allow_redirects=True)
        print("После перехода ->", r.url)

    if "releases.1c.ru" in r.url and r.status_code == 200:
        print("Успешно авторизовались на releases.1c.ru!")
        return True
    else:
        print("Не удалось войти на releases.1c.ru")
        return False


def get_urls_from_json() -> list:
    if not os.path.exists(LIST_FILE):
        print("Файл", LIST_FILE, "не найден!")
        return []

    with open(LIST_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            urls = []
            for item in data.get("components", []):
                url = item.get("url")
                if url:
                    urls.append(url)
            return urls
        except json.JSONDecodeError as e:
            print("Ошибка при чтении JSON:", e)
            return []

def get_urls_from_readme() -> list:
    if not os.path.exists(LIST_FILE):
        print("Файл", LIST_FILE, "не найден!")
        return []

    with open(LIST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "Компоненты используемые для тестирования"
    if start_marker not in content:
        print("Раздел 'Компоненты используемые для тестирования' не найден в README.md")
        return []

    section = content.split(start_marker, 1)[1].split("\n\n", 1)[0]

    urls = re.findall(r'https://releases\.1c\.ru/[^\s"\')]+', section)
    return list(dict.fromkeys(urls))


def get_direct_download_url(page_url: str) -> str:
    try:
        r = session.get(page_url, timeout=TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        link = soup.find("a", string=re.compile(r"Скачать дистрибутив", re.IGNORECASE))
        if link and link.get("href"):
            href = link["href"]
            if href.startswith("http"):
                return href
            else:
                return "https://releases.1c.ru" + href if href.startswith("/") else href
    except Exception as e:
        print("Ошибка при поиске 'Скачать дистрибутив':", e)

    return None


def download_file(url: str):
    print("Обрабатываем страницу:", url)

    direct_url = get_direct_download_url(url)
    if not direct_url:
        print("Ссылка 'Скачать дистрибутив' не найдена")
        return

    print("Найдена ссылка 'Скачать дистрибутив':", direct_url)

    # Получаем имя файла из заголовка
    try:
        head = session.head(direct_url, timeout=TIMEOUT, allow_redirects=True)
        content_disposition = head.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in content_disposition:
            match = re.search(r'filename\*?="?([^";]+)', content_disposition)
            if match:
                filename = match.group(1).strip().strip('"')
    except:
        filename = None

    if not filename:
        filename = os.path.basename(urlparse(direct_url).path)
        if not filename or "." not in filename:
            filename = "1c_file_" + str(int(time.time())) + ".zip"

    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Проверка на существование файла
    if os.path.exists(filepath):
        print("Файл уже существует, пропускаем")
        return

    print("Скачиваем файл...")
    try:
        with session.get(direct_url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=32*1024):
                    if chunk:
                        f.write(chunk)

        size_mb = os.path.getsize(filepath) // (1024 * 1024)
        print("Скачано:", filename, "(", size_mb, "МБ)")
    except Exception as e:
        print("Ошибка скачивания:", e)

def download_file_from_url(url: str):
    
    # Получаем имя файла из заголовка
    try:
        head = session.head(url, timeout=TIMEOUT, allow_redirects=True)
        content_disposition = head.headers.get("Content-Disposition", "")
        filename = None
        if "filename=" in content_disposition:
            match = re.search(r'filename\*?="?([^";]+)', content_disposition)
            if match:
                filename = match.group(1).strip().strip('"')
    except:
        filename = None

    if not filename:
        filename = os.path.basename(urlparse(url).path)
        if not filename or "." not in filename:
            filename = "1c_file_" + str(int(time.time())) + ".zip"

    filepath = os.path.join(DOWNLOAD_DIR, filename)

    # Проверка на существование файла
    if os.path.exists(filepath):
        print("Файл уже существует, пропускаем")
        return

    print("Скачиваем файл по ссылке:", url)
    try:
        with session.get(url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=32*1024):
                    if chunk:
                        f.write(chunk)
                        
        size_mb = os.path.getsize(filepath) // (1024 * 1024)
        print("Скачано:", filename, "(", size_mb, "МБ)")
    except Exception as e:
        print("Ошибка скачивания:", e)


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

    print("=== Авторизация на releases.1c.ru ===")
    username = input("Введите логин (обычно email): ").strip()
    password = getpass.getpass("Введите пароль: ")

    if not username or not password:
        print("Логин или пароль не введён. Выход.")
        exit(1)

    if not login_1c(username, password):
        print("Авторизация не удалась.")
        input("Нажмите Enter для выхода...")
        exit(1)

    urls = get_urls_from_json()

    if not urls:
        print("Не удалось найти ссылки в", LIST_FILE)
        input("Нажмите Enter...")
        exit(1)

    print("Найдено", len(urls), "ссылок для обработки.")

    for i, url in enumerate(urls, 1):
        print("[", i, "/", len(urls), "]")
        download_file_from_url(url)
        if i < len(urls):
            time.sleep(DELAY_BETWEEN_DOWNLOADS)

    print("Готово! Файлы сохранены в папку:", os.path.abspath(DOWNLOAD_DIR))
