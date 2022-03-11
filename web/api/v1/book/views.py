#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 10:55:39
LastEditors: xiangcai
LastEditTime: 2022-03-11 15:42:23
Description: file content
'''
import asyncio

from fastapi import APIRouter, Path, Form, Depends, \
    status, HTTPException, WebSocket, Response

from common.conts import SECOND
from web.codes import Code, codes_msg
from web.api.v1.book.models import Books
from web.api.connection import WebsocketManager
from web.api.validators import validate_page, validate_size
from web.api.v1.book.models import id_constraint, name_constraint, \
    author_constraint, year_constraint
from web.api.schema import default_object_responses, default_array_responses


book_data = Books()
router = APIRouter()


def validate_name(
    name: str = Form(..., **name_constraint)
):
    if name not in book_data.names:
        return name
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="book name already exists"
        )


@router.get("", responses=default_array_responses)
async def get_books(
    page: int = Depends(validate_page),
    size: int = Depends(validate_size)
):
    books = book_data.list(page, size)
    return {
        "code": Code.ok,
        "msg": codes_msg[Code.ok],
        "data": books
    }


@router.get("/{book_id}", responses=default_object_responses)
async def get_book(
    book_id: int = Path(..., **id_constraint)
):
    book = book_data.get(book_id)
    if not book:
        code = Code.unknown
    else:
        code = Code.ok
    return {
        "code": code,
        "msg": codes_msg[code],
        "data": book
    }


@router.post("", responses=default_object_responses)
async def add_book(
    name: str = Depends(validate_name),
    author: str = Form(..., **author_constraint),
    year: int = Form(..., **year_constraint)
):
    book = book_data.add(name, author, year)
    return {
        "code": Code.ok,
        "msg": codes_msg[Code.ok],
        "data": book
    }


@router.put("", responses=default_object_responses)
async def update_book(
    book_id: int = Form(..., **id_constraint),
    name: str = Form(None, **name_constraint),
    author: str = Form(None, **author_constraint),
    year: int = Form(None, **year_constraint)
):
    data = dict()
    if name:
        data["name"] = validate_name(name)
    if author:
        data["author"] = author
    if year:
        data["year"] = year
    book = book_data.update(book_id, data)
    if not book:
        code = Code.unknown
    else:
        code = Code.ok
    return {
        "code": code,
        "msg": codes_msg[code],
        "data": book
    }


@router.delete("/{book_id}", responses=default_object_responses)
async def del_book(
    book_id: int = Path(..., **id_constraint)
):
    book = book_data.del_book(book_id)
    if not book:
        code = Code.unknown
        return {
            "code": code,
            "msg": codes_msg[code],
            "data": book
        }
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.websocket("")
async def max_book_id(
    websocket: WebSocket
):
    async with WebsocketManager(websocket) as m:
        await m.send_message(str(book_data.max_id()))
        await asyncio.sleep(SECOND)


if __name__ == '__main__':
    pass
