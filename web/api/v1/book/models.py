#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2022-03-10 10:57:58
LastEditors: xiangcai
LastEditTime: 2022-03-11 10:08:25
Description: file content
'''
from threading import Lock
from datetime import datetime
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from web.api.validators import gen_constraint


id_constraint = gen_constraint(ge=1, description="book id", example=1)
name_constraint = gen_constraint(min_length=2, max_length=20, description="书名", example="我的世界")
author_constraint = gen_constraint(min_length=2, max_length=20, description="作者", example="佚名")
year_constraint = gen_constraint(ge=1970, le=datetime.now().year, description="发布年份", example=2022)


class Book(BaseModel):
    bid: int = Field(..., ge=1)
    name: str
    author: str
    year: int

    class Config:
        schema_extra = {
            "bid": 1,
            "name": "我的世界",
            "author": "佚名",
            "year": 2022
        }


class Books(object):

    def __init__(self):
        self.books = dict()
        self.next_id = 0
        self.lock = Lock()
        self.names = set()

    def add(self, name: str, author: str, year: int) -> Dict[str, Any]:
        with self.lock:
            self.next_id += 1
            book_id = self.next_id
            book = Book(
                bid=book_id,
                name=name,
                author=author,
                year=year
            )
            self.books[book_id] = book
            self.names.add(name)
        return book.dict()

    def del_book(self, book_id: int):
        if book_id not in self.books:
            return dict()
        with self.lock:
            book = self.books.pop(book_id)
            self.names.remove(book.name)
        return book.dict()

    def update(self, book_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        book = self.books.get(book_id)
        if book is None:
            return dict()
        with self.lock:
            ori_data = self.books.pop(book_id).dict()
            ori_name = ori_data.get("name")
            ori_data.update(data)
            self.books[book_id] = Book(**ori_data)
            name = data.get("name")
            if name is not None:
                self.names.remove(ori_name)
                self.names.add(name)
        return ori_data

    def get(self, book_id: int):
        book = self.books.get(book_id)
        if book is None:
            return dict()
        return book.dict()

    def list(self, page: int, size: int = 10) -> List[Dict[str, Any]]:
        books = list(self.books.values())[(page - 1) * size:page * size]
        return [book.dict() for book in books]

    def max_id(self) -> int:
        if self.books:
            book_id = list(self.books.keys())[-1]
        else:
            book_id = -1
        return book_id


if __name__ == '__main__':
    pass
