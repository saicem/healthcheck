#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import logging
from typing import Tuple
import requests
import random
import json

from requests.sessions import Session
from useragent import rand_agent


class HealthCheck:
    __province: str
    __city: str
    __county: str
    __street: str
    __json_data: dict
    __is_in_school: bool
    __is_leave_chengdu: bool
    __temperature_list = ["36°C以下", "36.5°C~36.9°C"]
    __cur_session: Session

    def __init__(
        self,
        nickname: str,
        sn: str,
        id_card: str,
        province: str,
        city: str,
        county: str,
        street: str,
        is_in_school: bool,
    ) -> None:
        self.__province = province
        self.__city = city
        self.__county = county
        self.__street = street
        self.__json_data = {"sn": sn, "idCard": id_card, "nickname": nickname}
        self.__is_in_school = is_in_school
        self.__is_leave_chengdu = bool(1 - is_in_school)
        self.__cur_session = requests.session()
        self.__cur_session.headers.setdefault("User-Agent", rand_agent())

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
    def get_session_id(self):
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/checkBind"
        resp = self.__cur_session.post(url=url, json=self.__json_data)
        session_id = json.loads(resp.text)["data"]["sessionId"]
        self.__cur_session.cookies.setdefault("JSESSIONID", session_id)
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
    def __get_bind_user_info(self) -> str:
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/bindUserInfo"
        resp = self.__cur_session.post(url=url, json=self.__json_data)
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
    def __submit_form(self) -> str:
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
            "isInSchool": int(self.__is_in_school),
            "isLeaveChengdu": int(self.__is_leave_chengdu),
            "isSymptom": "0",
            "temperature": random.choice(self.__temperature_list),
            "province": self.__province,
            "city": self.__city,
            "county": self.__county,
        }
        resp = self.__cur_session.post(url=url, json=json_data)
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
    def __cancel_bind(self):
        url = "https://zhxg.whut.edu.cn/yqtjwx/api/login/cancelBind"
        resp = self.__cur_session.post(url=url)
        logging.info(resp.text)

    # 健康填报全过程
    def health_check(self) -> Tuple[str, str]:
        self.get_session_id()
        json_bind = json.loads(self.__get_bind_user_info())
        print(json_bind)
        # 绑定是否成功
        if json_bind["status"]:
            user_data = json_bind["data"]["user"]
            json_check = json.loads(self.__submit_form())
            self.__cancel_bind()

            if json_check["status"]:
                return "填报成功", user_data
            else:
                # 今日已填报
                return json_check["message"], user_data
        else:
            self.__cancel_bind()
            # 该学号已被其它微信绑定 输入信息不符合
            return json_bind["message"], None
