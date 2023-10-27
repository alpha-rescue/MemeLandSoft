import requests
from playwright.sync_api import sync_playwright
from hashlib import md5
from random import choice
from string import digits
from time import time
import time as timess

def generate_random_number(length: int) -> int:
    return int(''.join([choice(digits) for _ in range(length)]))

def generate_csrf_token() -> str:
    random_int: int = generate_random_number(length=3)
    current_timestamp: int = int(str(int(time())) + str(random_int))
    random_csrf_token = md5(string=f'{current_timestamp}:{current_timestamp},{0}:{0}'.encode()).hexdigest()

    return random_csrf_token

def create_task(API_crt):
    url_create_task = f"https://api.1stcaptcha.com/funcaptchatokentask?apikey={API_crt}&sitekey=0152B4EB-D2DC-460A-89A1-629838B529C9&siteurl=https://twitter.com/account/access"

    responce_create_task = requests.get(url_create_task)
    if responce_create_task.json()["Code"] == 0 and responce_create_task.json()["Message"] == "OK":
        return responce_create_task.json()["TaskId"]
    else:
        raise Exception("Произошла ошибка с отправкой задания на решение капчи")

def get_task(API_crt, request_id):
    url_get_task = f"https://api.1stcaptcha.com/getresult?apikey={API_crt}&taskid={request_id}"

    for q in range(25):
        timess.sleep(2)
        responce_get_task = requests.get(url_get_task)
        if responce_get_task.json()["Code"] == 0 and responce_get_task.json()["Status"] == "SUCCESS":
            return responce_get_task.json()["Data"]["Token"]
        elif responce_get_task.json()["Code"] == 0 and responce_get_task.json()["Status"] == "PROCESSING":
            continue
        else:

            print(responce_get_task.json())
            raise Exception("Проблема с капчей при получение токена")


class twitter_unlock_v2:
    def __init__(self, auth_token, api_, proxies):
        self.auth_token = auth_token
        self.ct0_token = generate_csrf_token()
        self.API = api_
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            proxy={
               "server": f"{proxies.split(':')[0]}:{proxies.split(':')[1]}",
               "username": f"{proxies.split(':')[2]}",
               "password": f"{proxies.split(':')[3]}",
            }
        )
        self.context = self.browser.new_context()
        self.context.add_cookies([{"name": "auth_token", "value": f"{self.auth_token}", "domain": ".twitter.com", "path": "/", "expires": 1730076669.348026, "httpOnly": True, "secure": True, "sameSite": "None"},
                                  {"name": "ct0", "value": f"{self.ct0_token}", "domain": ".twitter.com", "path": "/", "expires": 1730076670.608594, "httpOnly": False, "secure": True, "sameSite": "Lax"}]
                                 )

        self.page = self.context.new_page()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.page.close()
        self.context.close()
        self.browser.close()
        self.playwright.stop()


    def check_and_succes_captcha(self): # проверка наличия фрейма и решение капчи
        for obj_frame in self.page.frames:
            if "game-core-frame" in str(obj_frame.name) or "game-core" in str(obj_frame.url):
                try:
                    id_task = create_task(self.API)
                    token_funcupc = get_task(self.API, id_task)
                    captcha_result = token_funcupc
                    self.page.evaluate(
                        'parent.postMessage(JSON.stringify({eventId:"challenge-complete",payload:{sessionToken:"' + captcha_result + '"}}),"*")')
                    break
                except:
                    id_task = create_task(self.API)
                    token_funcupc = get_task(self.API, id_task)
                    captcha_result = token_funcupc
                    self.page.evaluate(
                        'parent.postMessage(JSON.stringify({eventId:"challenge-complete",payload:{sessionToken:"' + captcha_result + '"}}),"*")')
                    break

    def click_on_start(self): #Проверка наличия кнопки старт и клик по ней
        try:
            # Ожидание появления элемента
            self.page.query_selector('input[type="submit"][value="Start"]').click(timeout=100)
        except:
            pass

    def click_on_continueTwitter(self):
        try:
            self.page.query_selector('input[type="submit"][value="Continue to Twitter"]').click(timeout=100)
        except:
            pass

    def click_Got_it(self):
        try:
            self.page.click('span:has-text("Got it")', timeout=100)
        except:
            pass

    def check_results(self):

        self.page.wait_for_timeout(5000)
        element_Home = self.page.query_selector('a[data-testid="AppTabBar_Home_Link"]') is not None
        element_exists_happinig = self.page.query_selector('div:has-text("What is happening?!")') is not None
        current_url = self.page.url
        if (element_exists_happinig == True and "https://twitter.com/home" in current_url) or (element_Home == True and "https://twitter.com/home" in current_url ):
            # print("Аккаунт разлочен")
            return True
        else:
#             print("Аккант не разлочен")
            pass
    def main_unlock_PW(self):
        # Загрузка страницы
        self.page.goto('https://twitter.com/', timeout=60000,
                       wait_until='domcontentloaded'
                       )
        self.page.wait_for_timeout(1000)
        for i in range(30):
            self.page.wait_for_timeout(1000)
            self.click_on_start()
            self.check_and_succes_captcha()
            self.click_on_continueTwitter()
            self.check_and_succes_captcha()
            self.click_Got_it()
            if self.check_results() == True:
                break



if __name__ == '__main__':

    ...

