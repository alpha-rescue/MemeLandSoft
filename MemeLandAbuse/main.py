import datetime
import random
import time
from threading import Thread
import tls_client.sessions
import ua_generator
import web3
from bs4 import BeautifulSoup
from eth_account.messages import encode_defunct
from web3.auto import w3

from TwitterModel import Account1
from config import refs, api_firstcaptcha, threads
from Unlocker import twitter_unlock_v2, generate_csrf_token


class MemeModel:

    def __init__(self, auth_token, ct0, proxy, authorization=None):

        self.auth_token = auth_token
        self.ct0 = ct0

        self.proxy_ = proxy

        proxy_log = proxy.split(':')[2]
        proxy_pass = proxy.split(':')[3]
        proxy_ip = proxy.split(':')[0]
        proxy_port = proxy.split(':')[1]

        self.session = self._make_scraper
        self.session.proxies = {'http': f'http://{proxy_log}:{proxy_pass}@{proxy_ip}:{proxy_port}',
                                'https': f'http://{proxy_log}:{proxy_pass}@{proxy_ip}:{proxy_port}'}
        self.ua = self.random_user_agent

        self.session.headers.update({
                                    'Origin': 'https://www.memecoin.org',
                                    'Referer': 'https://www.memecoin.org/',
                                     "User-Agent": self.ua})

        if authorization:
            self.session.headers.update({"Authorization": f"Bearer {authorization}"})

        self.tw_model = Account1(self.auth_token,
                                 self.ct0,
                                 proxy,
                                 "")

        self.points = 0

        self.result = self.tw_model.GetME()

    def GetUsername(self):

        self.session.headers.update({"content-type": None})
        response = self.session.get("https://memefarm-api.memecoin.org/user/info")
        # print(response.json())
        self.username = response.json()['twitter']['username']

    def AccountReger_v2(self):

        with self.session.get("https://memefarm-api.memecoin.org/user/twitter-auth?callback=https%3A%2F%2Fwww.memecoin.org%2Ffarming", allow_redirects=False) as response:

            url = response.headers['location']

            client_id = url.split('client_id=')[-1].split('&')[0]

            print(url)

            self.session.cookies.update({'auth_token': self.auth_token, 'ct0': self.ct0})

            with self.session.get(url, timeout=15, allow_redirects=False) as response:

                self.session.headers.update({
                    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                    'x-twitter-auth-type': 'OAuth2Session',
                    'x-csrf-token': self.ct0})

                # print(response.text)

                # self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                with self.session.get(
                        f'https://twitter.com/i/api/2/oauth2/authorize?code_challenge=challenge&code_challenge_method=plain&client_id={client_id}&redirect_uri=https%3A%2F%2Fwww.memecoin.org%2Ffarming&response_type=code&scope=users.read%20tweet.read%20offline.access&state=state',
                        timeout=15, allow_redirects=False) as response:
                    print(response.text)
                    code = response.json()['auth_code']

                    payload = {'approval': 'true', 'code': code}

                    self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})
                    with self.session.post('https://twitter.com/i/api/2/oauth2/authorize', data=payload,
                                           timeout=15) as response:
                        print(response.text)
                        url = response.json()['redirect_uri']
                        with self.session.get(url, timeout=15) as response:
                            print(response.text)

                    time.sleep(2)

                    self.session.headers.update({"content-type": "application/json"})

                    with self.session.post("https://memefarm-api.memecoin.org/user/twitter-auth", json={"code": code,
                                                                                                        "redirectUri": "https://www.memecoin.org/farming"}) as response:
                        print(response.text)
                        access_token = response.json()["accessToken"]

                        self.session.headers.update({"authorization": f"Bearer {access_token}"})


    def AccountRegistration(self):

        response =  self.session.get("https://memefarm-api.memecoin.org/user/twitter-auth?callback=https%3A%2F%2Fwww.memecoin.org%2Ffarming", allow_redirects=False)

        url = response.headers['Location']
        # print(url)

        while "https://api.twitter.com/oauth/authenticate?oauth_token=" not in url:
            response = self.session.get(
                "https://memefarm-api.memecoin.org/user/twitter-auth?callback=https%3A%2F%2Fwww.memecoin.org%2Ffarming",
                allow_redirects=False)

            url = response.headers['Location']

        oauth_token = url.split("oauth_token=")[-1]

        self.session.cookies.update({'auth_token': self.auth_token, 'ct0': self.ct0})
        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        response = self.session.get(url,allow_redirects=False)

        # print(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')
        authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')

        # print(authenticity_token)

        payload = {'authenticity_token': authenticity_token,
                   'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
                   'oauth_token': oauth_token}

        # self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
        response = self.session.post(f'https://api.twitter.com/oauth/authorize', data=payload, allow_redirects=True)
        # self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find('a', class_='maintain-context').get('href')
#         print(link)
        # self.session.headers.update({"authorization": None})

        oauth_verifier = link.split("oauth_verifier=")[-1]

        response = self.session.get(
                f"https://www.memecoin.org/farming?oauth_token={oauth_token}&oauth_verifier={oauth_verifier}",
                cookies={}, headers={"user-agent": self.ua,
                                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                                     "Accept-Encoding": "gzip, deflate, br",
                                     "Accept-Language": "en-US,en;q=0.9",
                                     "Dnt": "1",
                                     "Referer": "https://api.twitter.com/",
                                     "Sec-Ch-Ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                                     "Sec-Ch-Ua-Mobile": "?0",
                                     "Sec-Ch-Ua-Platform": '"Windows"',
                                     "Sec-Fetch-Dest": "document",
                                     "Sec-Fetch-Mode": "navigate",
                                     "Sec-Fetch-Site": "cross-site",
                                     "Upgrade-Insecure-Requests": "1"})

        time.sleep(2)

        self.memesession = tls_client.Session(client_identifier=random.choice([
                    'Chrome110',
                    'chrome111',
                    'chrome112'
                ]))

        self.memesession.headers.update({'user-agent': random.choice([
                                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
                                         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.962 YaBrowser/23.9.1.962 Yowser/2.5 Safari/537.36'
                                     ]),
                                     'Accept': 'application/json',
                                     'Accept-Language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7,cy;q=0.6',
                                     'Content-Type': 'application/json',
                                     'Origin': 'https://www.memecoin.org',
                                     'Referer': 'https://www.memecoin.org/'
                                     })
#         print(self.session.proxies)
        self.memesession.proxies = self.session.proxies

#         print(self.session.headers)

#         print({"oauth_token":oauth_token,"oauth_verifier":oauth_verifier})

        response = self.memesession.post("https://memefarm-api.memecoin.org/user/twitter-auth1", cookies={}, json={"oauth_token":oauth_token,"oauth_verifier":oauth_verifier})
        access_token = response.json()["accessToken"]

#         print(access_token)

        self.session.headers.update({"authorization": f"Bearer {access_token}",
                                     'user-agent': random.choice([
                                         'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
                                         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.962 YaBrowser/23.9.1.962 Yowser/2.5 Safari/537.36'
                                     ]),
                                         'accept': 'application/json',
                                         'accept-language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7,cy;q=0.6',
                                         'content-type': 'application/json',
                                         'origin': 'https://www.memecoin.org',
                                         'referer': 'https://www.memecoin.org/'
                                     })

    def MakeTaskWithName(self):

        name = self.result['name']
        location = self.result['location']
        description = self.result['description']

        with twitter_unlock_v2(self.auth_token, api_firstcaptcha, self.proxy_) as tw:
            tw.main_unlock_PW()

        if "♥️ Memecoin" not in name:
            self.tw_model.Update_profile_data(name+" ♥️ Memecoin",description,location)
            pass

        with twitter_unlock_v2(self.auth_token, api_firstcaptcha, self.proxy_) as tw:
            tw.main_unlock_PW()

        time.sleep(random.randint(5,10))

        while True:

            # print(self.session.headers)

            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/twitter-name")
#             print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue

            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]



    def MakeTask_TellTheWorld(self):

        # text = f"Hi, my name is @{self.username}, and I’m a $MEME (@Memecoin) farmer at @Memeland.\n\n"\
        #         "On my honor, I promise that I will do my best to do my duty to my own bag, and to farm #MEMEPOINTS at all times.\n\n"\
        #         "It ain’t much, but it’s honest work. 🧑‍🌾 "

        # self.tw_model.Tweet(text=text)

        time.sleep(random.randint(5,15))


        while True:
            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/share-message")

            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def MakeTask_Daily(self, param):

        # self.tw_model.Tweet(text=text)

        time.sleep(random.randint(5,15))

        while True:

            # print(self.session.headers)
            response = self.session.post(f"https://memefarm-api.memecoin.org/user/verify/daily-task/{param}")

            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def MakeTask_WhatIsMeme(self):

        text = f"👋 Excuse me Sir/Madam, do you have a moment to talk about @Memecoin? $MEME is literally a meme coin. No utility. No roadmap. No promises. No expectation of financial return. Just 100% memes. 😉 "

        self.tw_model.Tweet(text=text)

        time.sleep(random.randint(5,15))

        while True:
            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/daily-task/whatIsMeme")

            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def MakeTask_Follow_MemeLand(self):


        # self.tw_model.Follow(user_id="1491285218422300673")
        #
        # time.sleep(random.randint(5,15))

        payload = {"followId":"followMemeland"}

        while True:

            self.session.headers.update({"content-type": 'application/json'})

            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/twitter-follow", json=payload)

            self.session.headers.update({"content-type": None})

            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def MakeTask_Follow_MemeCoin(self):


        # self.tw_model.Follow(user_id="1518898059513835521")

        time.sleep(random.randint(5,15))

        payload = {"followId":"followMemecoin"}

        while True:

            self.session.headers.update({"content-type": 'application/json'})

            headers = {"Authorization": f"Bearer {self.auth_token}",
                       "Content-Type": "application/json",
                       "Dnt": "1",
                       "Origin": "https://www.memecoin.org",
                       "Referer": "https://www.memecoin.org/",
                       "Accept": "application/json",
                       "User-Agent": self.ua}
            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/twitter-follow", json=payload)
            self.session.headers.update({"content-type": None})
            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def MakeTask_Follow_9GagCeo(self):

        # self.tw_model.Follow(user_id="1493226085815025664")

        time.sleep(random.randint(5,15))

        payload = {"followId":"follow9gagceo"}

        while True:
            self.session.headers.update({"content-type": 'application/json'})
            headers = {"Authorization": f"Bearer {self.auth_token}",
                       "Content-Type": "application/json",
                       "Dnt": "1",
                       "Origin": "https://www.memecoin.org",
                       "Referer": "https://www.memecoin.org/",
                       "Accept": "application/json",
                       "User-Agent": self.ua}
            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/twitter-follow", json=payload)
            self.session.headers.update({"content-type": None})

            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def MakeTask_Follow_GmShowOfficial(self):

        # self.tw_model.Follow(user_id="1657048794931007494")

        time.sleep(random.randint(5,15))

        payload = {"followId":"followGMShowofficial"}

        while True:
            headers = {"Authorization": f"Bearer {self.auth_token}",
                       "Content-Type": "application/json",
                       "Dnt": "1",
                       "Origin": "https://www.memecoin.org",
                       "Referer": "https://www.memecoin.org/",
                       "Accept": "application/json",
                       "User-Agent": self.ua}
            self.session.headers.update({"content-type": 'application/json'})
            response = self.session.post("https://memefarm-api.memecoin.org/user/verify/twitter-follow", json=payload)
            self.session.headers.update({"content-type": None})

            # print(response.text)

            if response.json()['status'] != "success":
                time.sleep(random.randint(5,15))
                continue
            else:
                self.points = response.json()["points"]["current"]
                return response.json()["status"]

    def LinkWalletTask(self, private, address):

        address = web3.Web3.to_checksum_address(address)

        text = f"This wallet willl be dropped $MEME from your harvested MEMEPOINTS. If you referred friends, family, lovers or strangers, ensure this wallet has the NFT you referred.\n\nBut also...\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\nWallet: {address[:5]}...{address[-4:]}\nX account: @{self.username}"

        message = encode_defunct(text=text)
        signed_message = w3.eth.account.sign_message(message, private_key=private)
        self.signature = signed_message["signature"].hex()

        self.session.headers.update({"content-type": "application/json"})

        payload = {"address":address,
                   "delegate":address,
                   "message":text,
                   "signature":self.signature}

        response = self.session.post("https://memefarm-api.memecoin.org/user/verify/link-wallet", json=payload)
        self.session.headers.update({"content-type": None})

        self.points = response.json()["points"]["current"]
        return response.json()["status"]




    def InviteCodeTask(self):

        self.session.headers.update({"content-type": "application/json"})

        response = self.session.post("https://memefarm-api.memecoin.org/user/verify/invite-code", json={"code": random.choice(refs)})
        self.points = response.json()["points"]["current"]

        self.session.headers.update({"content-type": None})
        return response.json()["status"]

    @property
    def GetTasks(self):
        self.session.headers.update({'content-type': None})
        response = self.session.get("https://memefarm-api.memecoin.org/user/tasks")

        self.session.headers.update({'content-type': 'application/json'})
        return response.json()

    @property
    def GetPoints(self):

        with self.session.post("https://memefarm-api.memecoin.org/user/points/seen") as response:

            return response.json()["points"]["current"]

    @property
    def random_user_agent(self) -> str:

        return ua_generator.generate(device="desktop").text

    @property
    def _make_scraper(self):
        return tls_client.Session(
            client_identifier="chrome112",
            random_tls_extension_order=True
        )

def SaveLog(thread_name,auth_token,index,text):

    print(thread_name,"|",datetime.datetime.now(), "|",auth_token, "|", index, "|", text)
    with open(f"Logs/thread_{thread_name}.txt", "a+", encoding="utf-8") as file:
        file.write("{} {} {} {} {} {} {} {} {} {}".format(thread_name,"|",datetime.datetime.now(), "|",auth_token, "|", index, "|", text,'\n'))

def MultithreadStart(pool, thread_name):

    time.sleep(random.randint(100,300)/100)

    index = 1
    for item in pool:

        try:

            auth_token = item[0]
            # print(auth_token)
            ct0 = generate_csrf_token()
            proxy = item[2]
            authorization = None

            private = item[1]
            address = w3.eth.account.from_key(private).address

            # print(address)
            # input()

            # print(auth_token, proxy, private)

            SaveLog(thread_name, auth_token,index, "Старт")

            with twitter_unlock_v2(auth_token, api_firstcaptcha, proxy) as tw:
                tw.main_unlock_PW()

            MM = MemeModel(auth_token=auth_token,
                           ct0=ct0,
                           proxy=proxy,
                           authorization=authorization
                           )

            MM.AccountRegistration()
            MM.GetUsername()

            tasks = MM.GetTasks

            for task in tasks['tasks']:

                MM.session.headers.update({"content-type": None})

                if task['completed'] == False:

                    if task['id'] == 'linkWallet':
                        # print("linkWallet")
                        res = MM.LinkWalletTask(private, address)
                        if res:
                            SaveLog(thread_name, auth_token,index, "connect - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "connect - Ошибка")


                    elif task['id'] == 'twitterName':
                        #                         print("twitterName")

                        res = MM.MakeTaskWithName()
                        if res:
                            SaveLog(thread_name, auth_token,index, "twitterName - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "twitterName - Ошибка")

                    elif task['id'] == 'shareMessage':
                        #                         print("shareMessage")

                        res = MM.MakeTask_TellTheWorld()
                        if res:
                            SaveLog(thread_name, auth_token,index, "shareMessage - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "shareMessage - Ошибка")

                    elif task['id'] == 'inviteCode':
                        #                         print("inviteCode")

                        res = MM.InviteCodeTask()
                        if res:
                            SaveLog(thread_name, auth_token,index, "inviteCode - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "inviteCode - Ошибка")

                    elif task['id'] == 'followMemeland':
                        #                         print("followMemeland")

                        res = MM.MakeTask_Follow_MemeLand()
                        if res:
                            SaveLog(thread_name, auth_token,index, "followMemeland - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "followMemeland - Ошибка")

                    elif task['id'] == 'followMemecoin':
                        #                         print("followMemecoin")

                        res = MM.MakeTask_Follow_MemeCoin()
                        if res:
                            SaveLog(thread_name, auth_token,index, "followMemecoin - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "followMemecoin - Ошибка")

                    elif task['id'] == 'follow9gagceo':
                        #                         print("follow9gagceo")

                        res = MM.MakeTask_Follow_9GagCeo()
                        if res:
                            SaveLog(thread_name, auth_token,index, "follow9GagCeo - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "follow9GagCeo - Ошибка")

                    elif task['id'] == 'followGMShowofficial':
                        #                         print("followGMShowofficial")

                        res = MM.MakeTask_Follow_GmShowOfficial()
                        if res:
                            SaveLog(thread_name, auth_token,index, "followGMShowofficial - Готово")
                        else:
                            SaveLog(thread_name, auth_token,index, "followGMShowofficial - Ошибка")

                    time.sleep(random.randint(4, 10))

            for task in tasks['timely']:

                if task['completed'] == False:

                    res = MM.MakeTask_Daily(task['id'])
                    if res:
                        SaveLog(thread_name, auth_token,index, f"{task['id']} - Готово")
                    else:
                        SaveLog(thread_name, auth_token,index, f"{task['id']} - Ошибка")

            SaveLog(thread_name, auth_token,index, f"Поинтов: {MM.GetTasks['points']['current']}")
            SaveLog(thread_name, auth_token,index, '')

        except Exception as e:
            #
            # traceback.print_exc()

            SaveLog(thread_name, auth_token,index, f"Error ({str(e)})")
            SaveLog(thread_name, auth_token,index,'')

        index+=1

def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return list(lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


if __name__ == '__main__':

    twitter_data = []
    proxies = []
    addresses = []
    privates = []

    with open("Proxies.txt", "r") as file:
        for i in file:
            proxies.append(i.rstrip())

    with open("Twitters.txt", "r") as file:
        for i in file:
            twitter_data.append(i.rstrip())

    with open("Privates.txt", "r") as file:
        for i in file:
            privates.append(i.rstrip())

    data = []
    for index, item in enumerate(proxies):
        index = index
        data.append([twitter_data[index], privates[index], item])

    data = split_list(data, threads)

    thrs = []

    for index, i in enumerate(data):
        a = Thread(target=MultithreadStart, args=(i, index))
        thrs.append(a)

    for i in thrs:
        i.start()

    for i in thrs:
        i.join()


