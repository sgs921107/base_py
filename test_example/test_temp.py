#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: file content
'''
import pytest
import asyncio


class TestTemp(object):

    @pytest.mark.asyncio
    async def test_sync(self):
        pass

    def test_wait(self):
        pass


if __name__ == '__main__':
    pass
