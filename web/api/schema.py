#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 21:12:30
LastEditors: xiangcai
LastEditTime: 2022-03-11 15:36:02
Description: file content
'''
from fastapi import status


def successful_response(data_type: str, example=None):
    if example is None:
        if data_type == "object":
            example = dict()
        elif data_type == "array":
            example = list()
        else:
            example = ""
    return {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "schema": {
                    "title": "Successful",
                    "required": [
                        "code",
                        "msg",
                        "data"
                    ],
                    "type": "object",
                    "properties": {
                        "code": {
                            "title": "Code",
                            "type": "integer",
                        },
                        "msg": {
                            "title": "Message",
                            "type": "string"
                        },
                        "data": {
                            "title": "Data",
                            "type": data_type
                        }
                    }
                },
                "example": {
                    "code": 0,
                    "msg": "ok",
                    "data": example
                }
            }
        }
    }


default_object_responses = {
    status.HTTP_200_OK: successful_response("object")
}

default_array_responses = {
    status.HTTP_200_OK: successful_response("array")
}


if __name__ == '__main__':
    pass
