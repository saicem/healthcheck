#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import logging
from typing import Tuple
import requests
import random
import json

from requests.sessions import Session
from useragent import rand_agent


class HealthSubmit:
    __province: str
    __city: str
    __county: str
    __street: str
    __jsonData: dict
    __isInSchool: bool
    __isLeaveChengdu: bool
    __temperatureList = ["36°C以下", "36.5°C~36.9°C"]
    __curSession: Session

    def __init__(
        self,
        nickname: str,
        sn: str,
        idCard: str,
        province: str,
        city: str,
        county: str,
        street: str,
        isInSchool: bool,
    ) -> None:
        self.__province = province
        self.__city = city
        self.__county = county
        self.__street = street
        self.__jsonData = {"sn": sn, "idCard": idCard, "nickname": nickname}
        self.__isInSchool = isInSchool
        self.__isLeaveChengdu = bool(1 - isInSchool)
        self.__curSession = requests.session()
        self.__curSession.headers.setdefault("User-Agent", rand_agent())

    # 获取 data 下的 session_id 别的没什么卵用 至于检测绑定 code 参数来历不明
    # 已绑定
    # {
    #     "status": true,
    #     "code": 0,
    #     "message": null,
    #     "data": {
    #         "bind": false,
    #         "sessionId": "88888888-8888-8888-8888-888888888888"
    #     },
    #     "otherData": {}
    # }
    # 未绑定
    # {
    #     "status": true,
    #     "code": 0,
    #     "message": null,
    #     "data": {
    #         "bind": false,
    #         "sessionId": "88888888-8888-8888-8888-888888888888"
    #     },
    #     "otherData": {}
    # }
    def getSessionId(self):
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/checkBind"
        resp = self.__curSession.post(url=url, json=self.__jsonData)
        sessionId = json.loads(resp.text)["data"]["sessionId"]
        self.__curSession.cookies.setdefault("JSESSIONID", sessionId)
        logging.info(resp.text)

    # 绑定用户
    # 已被绑定
    # {
    #     "status": false,
    #     "code": 50000,
    #     "message": "该学号已被其它微信绑定",
    #     "data": null,
    #     "otherData": {}
    # }
    # 错误
    # {
    #     "status": false,
    #     "code": 50000,
    #     "message": "输入信息不符合",
    #     "data": null,
    #     "otherData": {}
    # }
    # 未绑定
    # {
    #     "status": true,
    #     "code": 0,
    #     "message": null,
    #     "data": {
    #         "user": {
    #             "id": 1***,
    #             "openId": "",
    #             "sn": "0************",
    #             "nickName": "青***",
    #             "gender": null,
    #             "language": null,
    #             "city": null,
    #             "province": null,
    #             "country": null,
    #             "avatarUrl": null,
    #             "createDate": "2021-88-88T88:88:88",
    #             "updateDate": "2021-88-88T88:88:88",
    #             "name": "**杰",
    #             "college": "**学院",
    #             "className": "公管**",
    #             "major": "公共**管理",
    #             "unionId": null
    #         }
    #     },
    #     "otherData": {}
    # }
    def __getBindUserInfo(self) -> str:
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/bindUserInfo"
        resp = self.__curSession.post(url=url, json=self.__jsonData)
        logging.info(resp.text)
        return resp.text

    # 提交表单
    # {
    #     "status": true,
    #     "code": 0,
    #     "message": null,
    #     "data": true,
    #     "otherData": {}
    # }
    # {
    #     "status": false,
    #     "code": 50000,
    #     "message": "今日已填报",
    #     "data": null,
    #     "otherData": {}
    # }
    def __submitForm(self) -> str:
        current_address = (
            str(self.__province)
            + str(self.__city)
            + str(self.__county)
            + str(self.__street)
        )
        url = "https://zhxg.whut.edu.cn/yqtjwx/./monitorRegister"
        json_data = {
            "diagnosisName": "",
            "relationWithOwn": "",
            "currentAddress": current_address,
            "remark": "无",
            "healthInfo": "正常",
            "isDiagnosis": 0,
            "isFever": 0,
            "isInSchool": int(self.__isInSchool),
            "isLeaveChengdu": int(self.__isLeaveChengdu),
            "isSymptom": "0",
            "temperature": random.choice(self.__temperatureList),
            "province": self.__province,
            "city": self.__city,
            "county": self.__county,
        }
        resp = self.__curSession.post(url=url, json=json_data)
        logging.info(resp.text)
        return resp.text

    # 取消绑定
    # {
    #     "status": true,
    #     "code": 0,
    #     "message": null,
    #     "data": "解绑成功",
    #     "otherData": {}
    # }
    # {
    #     "status": false,
    #     "code": 50000,
    #     "message": "解绑用户不存在",
    #     "data": null,
    #     "otherData": {}
    # }
    def __cancelBind(self):
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/cancelBind"
        resp = self.__curSession.post(url=url)
        logging.info(resp.text)

    # 健康填报全过程
    def submit(self) -> Tuple[str, str]:
        self.getSessionId()
        jsonBind = json.loads(self.__getBindUserInfo())
        print(jsonBind)
        # 绑定是否成功
        if jsonBind["status"]:
            userData = jsonBind["data"]["user"]
            jsonCheck = json.loads(self.__submitForm())
            self.__cancelBind()

            if jsonCheck["status"]:
                return "填报成功", userData
            else:
                # 今日已填报
                return jsonCheck["message"], userData
        else:
            self.__cancelBind()
            # 该学号已被其它微信绑定 输入信息不符合
            return jsonBind["message"], None
