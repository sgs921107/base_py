#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: file content
'''
import pytest

from common.conts import UTF8, LATIN1
from common.funcs import encrypt_md5, encrypt_sha1, encrypt_sha256, \
    gzip, ungzip, zlib, unzlib


class TestTemp(object):
    text = "这是一个测试this a test"
    content = text.encode(UTF8)

    def test_md5(self):
        want = "b690ebe899430b7c0417ae68c25806ff"
        text_have = encrypt_md5(self.text)
        assert text_have == want, "want text_have == %s, have %s" % (text_have, want)
        content_have = encrypt_md5(self.content)
        assert content_have == want, "want content_have == %s, have %s" % (content_have, want)

    def test_sha1(self):
        want = "9fbc46765c6b693cbe635b1130215e085ebe119d"
        text_have = encrypt_sha1(self.text)
        assert text_have == want, "want text_have == %s, have %s" % (text_have, want)
        content_have = encrypt_sha1(self.content)
        assert content_have == want, "want content_have == %s, have %s" % (content_have, want)

    def test_sha256(self):
        want = "2f941f227d1c471fcc90e48e9f1d538e9988da3951158fe5b74b4eacf14f4b79"
        text_have = encrypt_sha256(self.text)
        assert text_have == want, "want text_have == %s, have %s" % (text_have, want)
        content_have = encrypt_sha256(self.content)
        assert content_have == want, "want content_have == %s, have %s" % (content_have, want)

    def test_gzip(self):
        cipher_text = gzip(self.text)
        cipher_content = gzip(self.content)
        assert cipher_text == cipher_content, "want cipher_text == cipher_content, have (%s, %s)" % (cipher_text, cipher_content)
        have_text = ungzip(cipher_text)
        assert have_text == self.text, "want have_text == %s, have %s" % (self.text, have_text)
        have_content = ungzip(cipher_content.encode(LATIN1))
        assert have_content == self.text, "want have_content == %s, have %s" % (self.text, have_content)

    def test_zlib(self):
        cipher_text = zlib(self.text)
        cipher_content = zlib(self.content)
        assert cipher_text == cipher_content, "want cipher_text == cipher_content, have (%s, %s)" % (cipher_text, cipher_content)
        have_text = unzlib(cipher_text)
        assert have_text == self.text, "want have_text == %s, have %s" % (self.text, have_text)
        have_content = unzlib(cipher_content.encode(LATIN1))
        assert have_content == self.text, "want have_content == %s, have %s" % (self.text, have_content)

