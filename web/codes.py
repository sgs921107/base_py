#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 12:11:05
LastEditors: xiangcai
LastEditTime: 2022-03-10 12:13:20
Description: file content
'''
from dataclasses import dataclass


@dataclass
class Code:
    ok = 0
    unknown = 1000


codes_msg = {
    Code.ok: "ok",
    Code.unknown: "unknown error"
}


if __name__ == '__main__':
    pass
