import asyncio
import json
import random
import time
from asyncio import sleep
from urllib.parse import unquote

import aiohttp
import requests
from aiohttp_socks import ProxyConnector
from better_proxy import Proxy
from fake_useragent import UserAgent
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView

from data import config
from utils.core import logger


class DogsHouse:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.ref_code = 'RRQUZbFUQTGTu0N5hAueeg' if random.random() <= 0.3 else config.REF_LINK.split('startapp=')[1]
        self.reference, self.telegram_id = None, None
        self.proxy = f"{config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def logout(self):
        logger.info(f"sign {self.account} | loginOut")
        await self.session.close()

    async def login(self, proxy: Proxy):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        query = await self.get_tg_web_data()
        if query is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None, None
        param = unquote(query).split("&")
        pm = {}
        for iterating_var in param:
            kv = iterating_var.split("=")
            if kv[0] == 'user':
                pm[kv[0]] = json.loads(kv[1])
            else:
                pm[kv[0]] = kv[1]
        proxies = {
            "http": "socks5://" + proxy,
            "https": "socks5://" + proxy
        }
        head = {
            "Authorization": self.session.headers.get("Authorization"),
            "content-type": "application/json",
            "User-Agent": self.session.headers.get("User-Agent"),
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        #检测代理是否可用
        check_proxy_availability = requests.get("https://httpbin.org/ip", proxies=proxies)
        if check_proxy_availability.status_code == 200:
            ip = check_proxy_availability.json().get("origin")
            logger.info(f"sign {self.account} | Proxy IP: {ip}")
        #登录
        if self.session.headers.get("Authorization") is None:
            responses = requests.post('https://api.duckcoop.xyz/auth/telegram-login', json=pm, proxies=proxies,
                                      headers=head)
            head["Authorization"] = "Bearer " + json.loads(responses.text)['data']['token']
        #获取是否签到了
        responses = requests.get('https://api.duckcoop.xyz/checkin/get', proxies=proxies,
                                 headers=head)
        # 获取签到前金额
        total = requests.get('https://api.duckcoop.xyz/reward/get', proxies=proxies,
                                 headers=head)
        moneyBefore = json.loads(total.text)['data']['total']
        if json.loads(responses.text)['data']['can_claim']:
            # 进行签到
            responses = requests.post('https://api.duckcoop.xyz/checkin/claim', proxies=proxies,
                                      headers=head)
            if json.loads(responses.text)['data']['status']:
                # 获取签到后金额
                await asyncio.sleep(20)
                totalAfter = requests.get('https://api.duckcoop.xyz/reward/get', proxies=proxies,
                                     headers=head)
                moneyAfter = json.loads(totalAfter.text)['data']['total']
                logger.info(f"sign {self.account} | sign success,签到前：{moneyBefore},签到后:{moneyAfter}")
        await self.logout()
        return head.get("Authorization")

    async def goToTask1(self, proxy: Proxy,str):
        proxies = {
            "http": "socks5://" + proxy,
            "https": "socks5://" + proxy
        }
        head = {
            "Authorization": self.session.headers.get("Authorization"),
            "content-type": "application/json",
            "User-Agent": self.session.headers.get("User-Agent"),
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        head["Authorization"] = str
        done_my_list = []
        my_list = []
        # 获取已经过的任务id
        doneTaskList = requests.get('https://api.duckcoop.xyz/user-ambassador-mission/get', proxies=proxies,
                                    headers=head)
        dataList = json.loads(doneTaskList.text)['data']
        for element in dataList:
            done_my_list.append(element['ambassador_mission_id'])
        # 获取所有任务列表
        taskList = requests.get('https://api.duckcoop.xyz/ambassador-mission/list', proxies=proxies,
                                headers=head)
        resList = json.loads(taskList.text)['data']['data']
        # 检测代理是否可用
        check_proxy_availability = requests.get("https://httpbin.org/ip", proxies=proxies)
        if check_proxy_availability.status_code == 200:
            ip = check_proxy_availability.json().get("origin")
            logger.info(f"task {self.account} | Proxy IP: {ip}")
        for el in resList:
            partner_missions = el['ambassador_missions']
            for e in partner_missions:
                if e['am_id'] not in done_my_list:
                    my_list.append(e['am_id'])
        for  tk in my_list:
           try:
               pr = {
                   "ambassador_mission_id": tk
               }
               requests.post('https://api.duckcoop.xyz/user-ambassador-mission/claim', json=pr, proxies=proxies,
                             headers=head)
               time.sleep(1)
               taskAfter = requests.get('https://api.duckcoop.xyz/reward/get', proxies=proxies,
                                        headers=head)
               moneyTaskAfter = json.loads(taskAfter.text)['data']['total']
               logger.info(f"task {self.account} id:{tk} | task success, money:{moneyTaskAfter}")
           except:
               return None
    #做任务
    async def goTotask(self, proxy: Proxy,str):
        proxies = {
            "http": "socks5://" + proxy,
            "https": "socks5://" + proxy
        }
        head = {
            "Authorization": self.session.headers.get("Authorization"),
            "content-type": "application/json",
            "User-Agent": self.session.headers.get("User-Agent"),
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site"
        }
        head["Authorization"] =str
        done_my_list = []
        my_list = []
        #获取已经过的任务id
        doneTaskList = requests.get('https://api.duckcoop.xyz/user-partner-mission/get', proxies=proxies,
                                  headers=head)
        dataList = json.loads(doneTaskList.text)['data']
        for element in dataList:
            done_my_list.append(element['partner_mission_id'])
        #获取所有任务列表
        taskList = requests.get('https://api.duckcoop.xyz/partner-mission/list', proxies=proxies,
                                  headers=head)
        resList = json.loads(taskList.text)['data']['data']
        # 检测代理是否可用
        check_proxy_availability = requests.get("https://httpbin.org/ip", proxies=proxies)
        if check_proxy_availability.status_code == 200:
            ip = check_proxy_availability.json().get("origin")
            logger.info(f"task {self.account} | Proxy IP: {ip}")
        for el in resList:
            partner_missions =el['partner_missions']
            for e in partner_missions:
               if e['pm_id'] not in done_my_list:
                    my_list.append(e['pm_id'])
        for  tk in my_list:
           try:
               pr = {
                   "partner_mission_id": tk
               }
               requests.post('https://api.duckcoop.xyz/user-partner-mission/claim', json=pr, proxies=proxies,
                             headers=head)
               time.sleep(1)
               taskAfter = requests.get('https://api.duckcoop.xyz/reward/get', proxies=proxies,
                                        headers=head)
               moneyTaskAfter = json.loads(taskAfter.text)['data']['total']
               logger.info(f"task {self.account} id:{tk} | task success, money:{moneyTaskAfter}")
           except:
               return None
    #获取tg的重要信息
    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('duckscoop_bot'),
                bot=await self.client.resolve_peer('duckscoop_bot'),
                platform='android',
                from_bot_menu=False,
                url='https://app.duckcoop.xyz/',
            ))
            await self.client.disconnect()
            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query
        except:
            return None

