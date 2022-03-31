#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2021-12-03 10:39:21
LastEditors: xiangcai
LastEditTime: 2022-02-17 17:42:02
Description: file content
'''
import re
from typing import Union
from base64 import b64encode, b64decode

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from binascii import a2b_hex, b2a_hex

from common.conts import UTF8

PAD_ZERO = 1
PAD_PKCS7 = 2


def padding_zero(content: bytes, block_size=16) -> bytes:
    return content + (block_size - len(content) % block_size) * chr(0).encode()


def unpadding_zero(content: bytes) -> bytes:
    return content.rstrip(chr(0).encode())


def padding_pkcs7(content: bytes, block_size=16) -> bytes:
    padding_size = block_size - len(content) % block_size
    return content + padding_size * chr(padding_size).encode()


def unpadding_pkcs7(content: bytes) -> bytes:
    return content[:-ord(chr(content[-1]))]


class EncryptAES(object):

    pad_funcs = {
        PAD_ZERO: padding_zero,
        PAD_PKCS7: padding_pkcs7
    }

    unpad_funcs = {
        PAD_ZERO: unpadding_zero,
        PAD_PKCS7: unpadding_pkcs7
    }

    def __init__(
        self,
        cipher,
        # 填充方式
        pad_type: int = PAD_PKCS7,
        block_size: int = 16,
        encoding=UTF8
    ):
        self.cipher = cipher
        self.pad_type = pad_type
        self.encoding = encoding
        self.block_size = block_size

    @property
    def pad_func(self):
        func = self.pad_funcs.get(self.pad_type)
        if func is None:
            raise ValueError("pad type must in %s, have %s" % (self.pad_funcs.keys(), self.pad_type))
        return func

    @property
    def unpad_func(self):
        func = self.unpad_funcs.get(self.pad_type)
        if func is None:
            raise ValueError("pad type must in %s, have %s" % (self.pad_funcs.keys(), self.pad_type))
        return func

    def encrypt(self, text: str) -> str:
        # 字符串补位
        content = self.pad_func(text.encode(self.encoding), self.block_size)
        # 加密
        result = self.cipher.encrypt(content)
        # 将密文使用Base64进行编码后转为字符串类型
        return b64encode(result).decode(self.encoding)

    def decrypt(self, text: str) -> str:
        # 解密
        content = self.cipher.decrypt(b64decode(text))
        # 清除填充
        return self.unpad_func(content).decode(self.encoding)

    @classmethod
    def ecb_instance(
        cls,
        key: Union[str, bytes],
        pad_type: int = PAD_PKCS7,
        block_size: int = 16,
        encoding: str = UTF8
    ):
        return cls(
            AES.new(
                key.encode(encoding) if isinstance(key, str) else key,
                mode=1
            ),
            pad_type=pad_type,
            block_size=block_size,
            encoding=encoding
        )

    @classmethod
    def cbc_instance(
        cls,
        key: Union[str, bytes],
        iv: Union[str, bytes],
        pad_type: int = PAD_PKCS7,
        block_size: int = 16,
        encoding: str = UTF8
    ):
        # 同一实例只能做加密或解密
        return cls(
            AES.new(
                key.encode(encoding) if isinstance(key, str) else key,
                mode=2,
                IV=iv.encode(encoding) if isinstance(iv, str) else iv,
            ),
            pad_type=pad_type,
            block_size=block_size,
            encoding=encoding
        )


class EncryptRSA(object):
    key_compile = re.compile(r'^\s*(-----[a-zA-Z\s]+-----)\n*([a-zA-Z\d\s\n\+\=\/]+)\n*(-----[a-zA-Z\s]+-----)\s*$')

    def __init__(
        self,
        cipher,
        encoding: str = UTF8
    ) -> None:
        self.cipher = cipher
        self.encoding = encoding

    @classmethod
    def format_key(cls, rsa_key: str):
        """
        格式化rsa_key
        如果是pem格式的key则添加换行符
        """
        match_result = cls.key_compile.match(rsa_key)
        if match_result is None:
            return rsa_key
        return "\n".join(match_result.groups())

    def b64_encrypt(self, text: str) -> str:
        """
        加密后返回base64
        """
        cipher_content = self.cipher.encrypt(text.encode(self.encoding))
        return b64encode(cipher_content).decode(self.encoding)

    def b64_decrypt(self, cipher_text: str) -> Union[str, None]:
        """
        解密base64密文
        """
        content = self.cipher.decrypt(b64decode(cipher_text), None)
        return content and content.decode(self.encoding) or None

    def hex_encrypt(self, text: str) -> str:
        """
        加密后返回16进制字符串
        """
        cipher_content = self.cipher.encrypt(text.encode(self.encoding))
        return b2a_hex(cipher_content).decode(self.encoding)

    def hex_decrypt(self, cipher_text: str) -> Union[str, None]:
        """
        解密16进制密文
        """
        content = self.cipher.decrypt(a2b_hex(cipher_text), None)
        return content and content.decode(self.encoding) or None

    @classmethod
    def from_key(cls, externKey: str, passphrase: str = None):
        rsa_key = RSA.importKey(cls.format_key(externKey), passphrase)
        cipher = PKCS1_v1_5.new(rsa_key)
        return cls(cipher)

    @classmethod
    def from_construct(cls, construct):
        rsa_key = RSA.construct(construct)
        cipher = PKCS1_v1_5.new(rsa_key)
        return cls(cipher)


if __name__ == '__main__':
    pass
