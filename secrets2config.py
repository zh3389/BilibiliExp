# -*- coding: utf-8 -*-
# 用Secrets生成配置文件config.json

import json, os, re
from collections import OrderedDict

ADVCONFIG: str = os.environ.get('ADVCONFIG', None)

if ADVCONFIG:
    with open('./config/config.json','w',encoding='utf-8') as fp:
        fp.write(ADVCONFIG)

BILICONFIG: str = os.environ.get('BILICONFIG', None)
PUSH_MESSAGE: str = os.environ.get('PUSH_MESSAGE', None)

if not (BILICONFIG or ADVCONFIG):
    print("secrets(BILICONFIG)和secrets(ADVCONFIG)至少填写一个")
    exit(-1)

with open('./config/config.json','r',encoding='utf-8') as fp:
    configData: dict = json.loads(re.sub(r'\/\*[\s\S]*?\*\/', '', fp.read()), object_pairs_hook=OrderedDict)

if BILICONFIG:
    SESSDATA, bili_jct, DedeUserID = False, False, False
    users = []
    cookieDatas = {}
    for x in BILICONFIG.split("\n"):
        cookie = x.strip().replace(",", "%2C")
        if re.match("[a-z0-9]{8}%2C[0-9a-z]{10}%2C[a-z0-9]{5}\*[a-z0-9]{2}", cookie):
            cookieDatas["SESSDATA"] = cookie
            SESSDATA = True
        elif re.match("[a-z 0-9]{31}", cookie):
            cookieDatas["bili_jct"] = cookie
            bili_jct = True
        elif re.match("^[0-9]*$", cookie):
            cookieDatas["DedeUserID"] = cookie
            DedeUserID = True
        if SESSDATA and bili_jct and DedeUserID:
            users.append({"cookieDatas": cookieDatas.copy(), "tasks": {}})
            SESSDATA, bili_jct, DedeUserID = False, False, False
    if len(users) == 0:
        print("虽然配置了BILICONFIG，但并没有发现有效账户cookie，如有必要请使用首页的复杂部署模式，并配置ADVCONFIG")
        exit(-1)
    else:
        configData["users"] = users

if PUSH_MESSAGE:
    if not 'webhook' in configData:
        configData["webhook"] = {
            "http_header": {"User-Agent":"Mozilla/5.0"},
            "variable": {
                "msg_simple": None,
                "title": "B站经验脚本消息推送"
                }
            }
    i = 0
    webhooks = []
    for x in PUSH_MESSAGE.split("\n"):
        value = x.strip()
        if x.startswith("SCU"):
            i += 1
            webhooks.append({
                "name": f"server酱消息推送{i}",
                "msg_separ": r"\n\n",
                "method": 1,
                "url": f"https://sc.ftqq.com/{value}.send",
                "params": {
                    "text": "{title}",
                    "desp": "{msg_simple}" 
                }
            })
        elif re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", value):
            i += 1
            webhooks.append({
                "name": f"邮箱消息推送{i}",
                "msg_separ": r"<br>",
                "method": 0,
                "url": "http://liuxingw.com/api/mail/api.php",
                "params": {
                    "address": value,
                    "name": "{title}",
                    "certno": "{msg_simple}" 
                }
            })
        else:
            ma = re.match("^([0-9]{7,11}:[0-9 a-z A-Z]*),(.*)$", value)
            if ma:
                i += 1
                ma = ma.groups()
                webhooks.append({
                    "name": f"telegram_bot消息推送{i}",
                    "method": 1,
                    "url": f"https://api.telegram.org/bot{ma[0]}/sendMessage",
                    "params": {
                        "chat_id": ma[1],
                        "text": "{msg_simple}" 
                    }
                })
    configData["webhook"]["hooks"] = webhooks

with open('./config/config.json','w',encoding='utf-8') as fp:
    json.dump(configData, fp, ensure_ascii=False)
