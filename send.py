#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import requests
import config

params = {"qq": config.bot_qq, "funcname": "SendMsgV2"}


# 利用qq机器人发送消息
def sendQqMsg(qq: str, msg: str):
    json = {
        "ToUserUid": qq,
        "SendToType": 1,
        "SendMsgType": "TextMsg",
        "Content": msg,
    }

    res = requests.post(url=config.bot_msg_url, params=params, json=json)
