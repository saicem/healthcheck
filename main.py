#!/usr/bin/env python3
# -*-coding:utf-8 -*-
from health import HealthSubmit
import logging
from send import sendQqMsg
import json
import config
import time

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

    def __init__(self, ls) -> None:
        self.nickname = ls[1]
        self.sn = ls[2]
        self.id_card = ls[3]
        self.province = ls[4]
        self.city = ls[5]
        self.county = ls[6]
        self.street = ls[7]
        self.isInSchool = ls[8]


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
    userInfoJson = open(config.json_file, "r", encoding="utf8").read()
    userInfo = json.loads(userInfoJson)

    for info in userInfo:

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
        ).submit()

        if msg == "填报成功" or msg == "今日已填报":
            sendQqMsg(info[0], "{},{}".format(user_data["name"], msg))
        else:
            sendQqMsg(info[0], msg)

        time.sleep(1)
