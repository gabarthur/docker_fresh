import requests
import os
import time
import re
import getpass
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import platform

OS_TYPE = ("Windows" if platform.system() == "Windows"
           else "Linux" if platform.system() == "Linux"
           else "other")
if OS_TYPE == "Linux":
    OS_NAME = platform.version()
OS_ARCHITECTURE = platform.machine()

OS_TYPE = "Linux"             #УДАЛИТЬ!!!
OS_NAME = "Ubuntu"            #УДАЛИТЬ!!!
OS_VERSION = "22.04"          #УДАЛИТЬ!!!
#if OS_NAME == "other":
#    print("Установка на данной ОС не поддерживается. Завершение...")
#    sys.exit(1)

DOWNLOAD_DIR = "distr"

TIMEOUT = 60
DELAY_BETWEEN_DOWNLOADS = 1

BASE_URL = "https://releases.1c.ru"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
})

necessary_components = [
    r"^Менеджер сервиса\. Версия .+?\. Полный дистрибутив$",
    r"^Агент сервиса\. Версия .+?\. Полный дистрибутив$",
    r"^Управление службой поддержки, версия .+?\. Полный дистрибутив$",
    r"^Менеджер доступности, версия .+?\. Полный дистрибутив$",
    r"^Сайт, версия .+?\. DEB, RPM для Linux и WAR-файл в одном архиве$",
    r"^Форум, версия .+?\. DEB, RPM для Linux и WAR-файл в одном архиве$",
    r"^Шлюз приложений, версия .+?\. DEB, RPM для Linux и JAR-файл в одном архиве$",
    r"^Страница недоступности, версия .+?\. DEB, RPM для Linux и WAR в одном архиве$",
    r"^Сервер исполнителя скриптов подсистемы 1С:Фреш, версия .*$",
    r"^Приложение 1С:Шины, версия .*$",
    r"^.*Дистрибутив 1С:Исполнитель \(U\).*$",
    rf"^.*Сервер взаимодействия \(64-bit\).*{OS_TYPE}.*$",
    rf"^.*Сервер 1С:Шины со средой разработки для ОС.*{OS_TYPE}.*$",
    rf"^.*Дистрибутив СУБД PostgreSQL для {OS_NAME} {OS_VERSION} {OS_ARCHITECTURE} (64-bit) одним архивом (ручная установка).*$"
]

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

def get_urls_from_page(url: str) -> list:
    try:
        r = session.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        links = soup.find_all("a", href=True)
        urls = {}
        for link in links:
            #print(link.text.strip(), "->", link['href'])
            href = link['href']
            if href.startswith("/version_file") and any(re.fullmatch(pattern, link.text) for pattern in necessary_components):
                urls[link.text] = href
        return urls
    except Exception as e:
        print("Ошибка при получении URL-ов:", e)
        return []

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
                return BASE_URL + href if href.startswith("/") else href
    except Exception as e:
        print("Ошибка при поиске 'Скачать дистрибутив':", e)

    return None

def download_file(url: str):
    
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
        print("Скачано:", filename, "(" + str(size_mb) + " МБ)")
    except Exception as e:
        print("Ошибка скачивания:", e)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

    print("=== Авторизация на releases.1c.ru ===")
    username = input("Введите логин (обычно email): ").strip()
    password = getpass.getpass("Введите пароль: ")
    print("=== Указание версий компонентов ===")
    technology_version = input("Введите версию облачной подсистемы Фреш (оставьте пустым, чтобы использовать версию по умолчанию): ").strip()
    if technology_version == "":
        technology_version = "1.0.51.1"
    technology_page = f"{BASE_URL}/version_files?nick=FreshPublic&ver={technology_version}"

    script_version = input("Введите версию 1С:Предприятие.Элемент Скрипт (оставьте пустым, чтобы использовать версию по умолчанию): ").strip()
    if script_version == "":
        script_version = "3.0.2.2"
    script_page = f"{BASE_URL}/version_files?nick=Script&ver={script_version}"

    collaboration_system_version = input("Введите версию 1С:Сервер Взаимодействия (оставьте пустым, чтобы использовать версию по умолчанию): ").strip()
    if collaboration_system_version == "":
        collaboration_system_version = "27.0.42"
    collaboration_system_page = f"{BASE_URL}/version_files?nick=CollaborationSystem&ver={collaboration_system_version}"

    bus_version = input("Введите версию 1С:Шина (оставьте пустым, чтобы использовать версию по умолчанию): ").strip()
    if bus_version == "":
        bus_version = "7.1.7"
    bus_page = f"{BASE_URL}/version_files?nick=esb&ver={bus_version}"

    postgre_version = input("Введите версию PostgreSQL (оставьте пустым, чтобы использовать версию по умолчанию): ").strip()
    if postgre_version == "":
        postgre_version = "17.8-1.1C"
    postgre_page = f"{BASE_URL}/version_files?nick=PostgreSQL&ver={postgre_version}"

    if not login_1c(username, password):
        print("Авторизация не удалась.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    technology_urls = get_urls_from_page(technology_page)
    for name, url in technology_urls.items():
        download_url = get_direct_download_url(BASE_URL + url)
        if download_url:
            print(f"Скачиваем компонент: {name}")
            download_file(download_url)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    script_urls = get_urls_from_page(script_page)
    for name, url in script_urls.items():
        download_url = get_direct_download_url(BASE_URL + url)
        if download_url:
            print(f"Скачиваем компонент: {name}")
            download_file(download_url)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    collaboration_system_urls = get_urls_from_page(collaboration_system_page)
    for name, url in collaboration_system_urls.items():
        download_url = get_direct_download_url(BASE_URL + url)
        if download_url:
            print(f"Скачиваем компонент: {name}")
            download_file(download_url)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    bus_urls = get_urls_from_page(bus_page)
    for name, url in bus_urls.items():
        download_url = get_direct_download_url(BASE_URL + url)
        if download_url:
            print(f"Скачиваем компонент: {name}")
            download_file(download_url)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)

    '''postgre_urls = get_urls_from_page(postgre_page)
    for name, url in postgre_urls.items():
        download_url = get_direct_download_url(BASE_URL + url)
        if download_url:
            print(f"Скачиваем компонент: {name}")
            download_file(download_url)
        time.sleep(DELAY_BETWEEN_DOWNLOADS)'''