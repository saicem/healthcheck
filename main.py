#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from health import HealthSubmit
import logging
from send import sendQqMsg
import time
from user_info import USER_INFO

logging.basicConfig(
    format="%(levelname)s: %(asctime)s - %(filename)s:%(module)s[line:%(lineno)d] - %(message)s",
    level=logging.INFO,
    filename="health.log",
    filemode="a",
)


class HealthCheckForm:
    nickname: str
    sn: str
    id_card: str
    province: str
    city: str
    county: str
    street: str
    isInSchool: bool
    isInWuhan: bool

    def __init__(self, userInfo: dict) -> None:
        self.nickname = userInfo["wx_name"]
        self.sn = userInfo["stu_id"]
        self.id_card = userInfo["password"]
        self.province = userInfo["province"]
        self.city = userInfo["city"]
        self.county = userInfo["county"]
        self.street = userInfo["street"]
        self.isInSchool = userInfo["isInSchool"]
        self.isInWuhan = userInfo["isInWuhan"]


# data
# {
#     "status": True,
#     "code": 0,
#     "message": None,
#     "data": {
#         "user": {
#             "id": 19**,
#             "openId": "",
#             "sn": "012**",
#             "nickName": "青*",
#             "gender": None,
#             "language": None,
#             "city": None,
#             "province": None,
#             "country": None,
#             "avatarUrl": None,
#             "createDate": "2021-88-88T88:88:88",
#             "updateDate": "2021-88-88T88:88:88",
#             "name": "**杰",
#             "college": "**学院",
#             "className": "公管**",
#             "major": "公共**管理",
#             "unionId": None,
#         }
#     },
#     "otherData": {},
# }
if __name__ == "__main__":

    for info in USER_INFO:

        check_form = HealthCheckForm(info)

        msg, user_data = HealthSubmit(
            check_form.nickname,
            check_form.sn,
            check_form.id_card,
            check_form.province,
            check_form.city,
            check_form.county,
            check_form.street,
            check_form.isInSchool,
            check_form.isInWuhan,
        ).submit()

        if msg == "填报成功" or msg == "今日已填报":
            sendQqMsg(info["qq"], "{},{}".format(user_data["name"], msg))
        else:
            sendQqMsg(info["qq"], msg)

        time.sleep(1)
