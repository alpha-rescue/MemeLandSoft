
import random
import ssl

import cloudscraper
import requests

def random_user_agent():
    browser_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{2}_{3}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{1}.{2}) Gecko/20100101 Firefox/{1}.{2}',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Edge/{3}.{4}.{5}'
    ]

    chrome_version = random.randint(70, 108)
    firefox_version = random.randint(70, 108)
    safari_version = random.randint(605, 610)
    edge_version = random.randint(15, 99)

    chrome_build = random.randint(1000, 9999)
    firefox_build = random.randint(1, 100)
    safari_build = random.randint(1, 50)
    edge_build = random.randint(1000, 9999)

    browser_choice = random.choice(browser_list)
    user_agent = browser_choice.format(chrome_version, firefox_version, safari_version, edge_version, chrome_build, firefox_build, safari_build, edge_build)

    return user_agent

class Account1:

    def __init__(self, auth_token, csrf, proxy, name):

        self.name = name

        proxy_log = proxy.split(':')[2]
        proxy_pass = proxy.split(':')[3]
        proxy_ip = proxy.split(':')[0]
        proxy_port = proxy.split(':')[1]

        self.session = self._make_scraper()
        self.session.proxies = {'http': f'http://{proxy_log}:{proxy_pass}@{proxy_ip}:{proxy_port}',
                                'https': f'http://{proxy_log}:{proxy_pass}@{proxy_ip}:{proxy_port}'}
        self.session.user_agent = random_user_agent()

        adapter = requests.adapters.HTTPAdapter(max_retries=2)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        authorization_token = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'

        self.csrf = csrf
        self.auth_token = auth_token
        self.cookie = f'auth_token={self.auth_token}; ct0={self.csrf}'

        liketweet_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {authorization_token}',
            'x-csrf-token': self.csrf,
            'cookie': self.cookie
        }

        self.session.headers.update(liketweet_headers)

        # print('Аккаунт готов')

    # Основные функции твиттер аккаунта

    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )


    def Tweet(self, text, mediaIds=None, media_group=None):

        if mediaIds == None:

            payload = {"variables": {
                "tweet_text": text,
                "dark_request": False,
                "media": {
                    "media_entities": [],  # {'media_id': ..., 'tagged_users': []}
                    "possibly_sensitive": False
                },
                "withDownvotePerspective": False,
                "withReactionsMetadata": False,
                "withReactionsPerspective": False,
                "withSuperFollowsTweetFields": True,
                "withSuperFollowsUserFields": True,
                "semantic_annotation_ids": []
            }, "features": {
                "tweetypie_unmention_optimization_enabled": True,
                "vibe_api_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "interactive_text_enabled": True,
                "responsive_web_text_conversations_enabled": False,
                "responsive_web_twitter_blue_verified_badge_is_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": False,
                "verified_phone_label_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": False,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "responsive_web_enhance_cards_enabled": False
            },
                "queryId": "Tz_cZL9zkkY2806vRiQP0Q"
            }

            with self.session.post("https://api.twitter.com/graphql/Tz_cZL9zkkY2806vRiQP0Q/CreateTweet", json=payload,
                                   timeout=30) as response:
                print(response.text)
                pass


        else:

            payload = {"variables": {
                "tweet_text": text,
                "dark_request": False,
                "media": {
                    "media_entities": [{'media_id': str(self.Upload_image(f'Media/{mediaId}.jpg' if media_group == None else f'Media/{media_group}/{mediaId}.jpg')),
                                        'tagged_users': []} for mediaId in mediaIds],
                    # {'media_id': ..., 'tagged_users': []}
                    "possibly_sensitive": False
                },
                "semantic_annotation_ids": []
            }, "features":
                {"tweetypie_unmention_optimization_enabled": True,
                 "vibe_api_enabled": True,
                 "responsive_web_edit_tweet_api_enabled": True,
                 "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                 "view_counts_everywhere_api_enabled": True,
                 "longform_notetweets_consumption_enabled": True,
                 "tweet_awards_web_tipping_enabled": False,
                 "interactive_text_enabled": True,
                 "responsive_web_text_conversations_enabled": False,
                 "longform_notetweets_rich_text_read_enabled": True,
                 "blue_business_profile_image_shape_enabled": True,
                 "responsive_web_graphql_exclude_directive_enabled": True,
                 "verified_phone_label_enabled": False,
                 "freedom_of_speech_not_reach_fetch_enabled": False,
                 "standardized_nudges_misinfo": True,
                 "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
                 "responsive_web_graphql_timeline_navigation_enabled": True,
                 "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                 "responsive_web_enhance_cards_enabled": False},
                "queryId": "7TKRKCPuAGsmYde0CudbVg"
            }

            self.session.headers.update({'content-type': 'application/json'})
            with self.session.post("https://api.twitter.com/graphql/7TKRKCPuAGsmYde0CudbVg/CreateTweet", json=payload,
                                   timeout=30) as response:
                # print(response.text)
                pass


    def Update_profile_data(self, name, description, location):

        payload = {'displayNameMaxLength': 50,
                   'name': name,
                   'description': description,
                   'location': location}

        self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})

        with self.session.post('https://api.twitter.com/1.1/account/update_profile.json', data=payload,
                               timeout=20) as response:
            # print(response.text)
            return


    def Get_User_Id(self, name):

        with self.session.get(f'https://api.twitter.com/1.1/users/show.json?screen_name={name}', timeout=10, allow_redirects=True) as response:

            return response.json()['id_str']

    def GetME(self):

        with self.session.get('https://api.twitter.com/1.1/account/verify_credentials.json') as response:
            # print(response.text)
            return response.json()


    def Get_User_Username(self, id):

        with self.session.get(f'https://api.twitter.com/1.1/users/show.json?user_id={id}', timeout=10, allow_redirects=True) as response:

            return response.json()['screen_name']



if __name__ == '__main__':
    ...