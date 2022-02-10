#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-01-10 15:19:43
LastEditors: xiangcai
LastEditTime: 2022-02-10 17:23:17
Description: file content
'''

from random import choice

os_storeage = [
    "Macintosh; Intel Mac OS X 10_10",
    "Windows NT 10.0",
    "Windows NT 5.1",
    "Windows NT 6.1; WOW64",
    "Windows NT 6.1; Win64; x64",
    "X11; Linux x86_64",
]

# 火狐浏览器版本列表
firefox_versions = [
    "35.0",
    "40.0",
    "41.0",
    "44.0",
    "45.0",
    "48.0",
    "48.0",
    "49.0",
    "50.0",
    "52.0",
    "52.0",
    "53.0",
    "54.0",
    "56.0",
    "57.0",
    "57.0",
    "58.0",
    "58.0",
    "59.0",
    "60.0",
    "60.0",
    "61.0",
    "63.0",
]

chrome_versions = [
    "37.0.2062.124",
    "40.0.2214.93",
    "41.0.2228.0",
    "49.0.2623.112",
    "55.0.2883.87",
    "56.0.2924.87",
    "57.0.2987.133",
    "61.0.3163.100",
    "63.0.3239.132",
    "64.0.3282.0",
    "65.0.3325.146",
    "68.0.3440.106",
    "69.0.3497.100",
    "70.0.3538.102",
    "74.0.3729.169",
]

opera_versions = [
    "2.7.62 Version/11.00",
    "2.2.15 Version/10.10",
    "2.9.168 Version/11.50",
    "2.2.15 Version/10.00",
    "2.8.131 Version/11.11",
    "2.5.24 Version/10.54",
]

uc_web_versinos = [
    "10.9.8.1006",
    "11.0.0.1016",
    "11.0.6.1040",
    "11.1.0.1041",
    "11.1.1.1091",
    "11.1.2.1113",
    "11.1.3.1128",
    "11.2.0.1125",
    "11.3.0.1130",
    "11.4.0.1180",
    "11.4.1.1138",
    "11.5.2.1188",
]

uc_web_devices = [
    "SM-C111",
    "SM-J727T1",
    "SM-J701F",
    "SM-J330G",
    "SM-N900",
    "DLI-TL20",
    "LG-X230",
    "AS-5433_Secret",
    "IdeaTabA1000-G",
    "GT-S5360",
    "HTC_Desire_601_dual_sim",
    "ALCATEL_ONE_TOUCH_7025D",
    "SM-N910H",
    "Micromax_Q4101",
    "SM-G600FY",
]

android_versions = [
    "4.4.2",
    "4.4.4",
    "5.0",
    "5.0.1",
    "5.0.2",
    "5.1",
    "5.1.1",
    "5.1.2",
    "6.0",
    "6.0.1",
    "7.0",
    "7.1.1",
    "7.1.2",
    "8.0.0",
    "8.1.0",
    "9.0",
]

nexus10_builds = [
    "JOP40D",
    "JOP40F",
    "JVP15I",
    "JVP15P",
    "JWR66Y",
    "KTU84P",
    "LMY47D",
    "LMY47V",
    "LMY48M",
    "LMY48T",
    "LMY48X",
    "LMY49F",
    "LMY49H",
    "LRX21P",
    "NOF27C",
]

nexus10_safari = [
    "534.30",
    "535.19",
    "537.22",
    "537.31",
    "537.36",
    "600.1.4",
]


class UserAgentFactory(object):
    _instance = None
    _mobile_instance = None

    def __init__(self, is_mobile=False) -> None:
        self.gen_ua_funcs = is_mobile and [
            self.gen_mobile_uc_ua,
            self.gen_mobile_nexus10_ua
        ] or [
            self.gen_chrome_ua,
            self.gen_firefox_ua,
            self.gen_opera_ua
        ]

    @classmethod
    def __new__(cls, *args, **kwargs):
        if args and args[0] is True or kwargs.get("is_mobile") is True:
            if cls._mobile_instance is None:
                cls._mobile_instance = super().__new__(cls)
            return cls._mobile_instance
        else:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    @staticmethod
    def choice_os():
        return choice(os_storeage)

    def gen_firefox_ua(self):
        os = self.choice_os()
        version = choice(firefox_versions)
        return "Mozilla/5.0 (%s; rv:%s) Gecko/20100101 Firefox/%s" % (os, version, version)

    def gen_chrome_ua(self):
        os = self.choice_os()
        version = choice(chrome_versions)
        return "Mozilla/5.0 (%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36" % (os, version)

    def gen_opera_ua(self):
        os = self.choice_os()
        version = choice(opera_versions)
        return "Opera/9.80 (%s; U; en) Presto/%s" % (os, version)

    @staticmethod
    def choice_android_version():
        return choice(android_versions)

    def gen_mobile_uc_ua(self):
        android = self.choice_android_version()
        device = choice(uc_web_devices)
        version = choice(uc_web_versinos)
        return "UCWEB/2.0 (Java; U; MIDP-2.0; Nokia203/20.37) U2/1.0.0 UCMini/%s (SpeedMode; Proxy; Android %s; %s ) U2/1.0.0 Mobile" % (version, android, device)

    def gen_mobile_nexus10_ua(self):
        android = self.choice_android_version()
        build = choice(nexus10_builds)
        chrome = choice(chrome_versions)
        safari = choice(nexus10_safari)
        return "Mozilla/5.0 (Linux; Android %s; Nexus 10 Build/%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/%s" % (android, build, chrome, safari)

    def gen_ua(self):
        return choice(self.gen_ua_funcs)()


if __name__ == '__main__':
    pass
