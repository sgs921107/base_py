#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2021-12-03 10:39:21
LastEditors: xiangcai
LastEditTime: 2022-02-10 19:10:38
Description: file content
'''
from re import compile
from typing import Union
from base64 import b64encode, b64decode

from Crypto.PublicKey import RSA
from binascii import a2b_hex, b2a_hex
from Crypto.Cipher import PKCS1_v1_5, AES

from common.conts import UTF8

PAD_ZERO = 1
PAD_PKCS7 = 2


def padding_zero(data: str, block_size=16):
    return data + (block_size - len(data) % block_size) * chr(0)


def unpadding_zero(data: str):
    return data.rstrip("0")


def padding_pkcs7(data: str, block_size=16):
    return data + (block_size - len(data) % block_size) * chr(block_size - len(data) % block_size)


def unpadding_pkcs7(data: str):
    return data[:-ord(data[-1])]


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
        # 密钥
        self, key: str,
        # 偏移量
        iv: Union[str, None] = None,
        # 填充方式
        pad_type: int = PAD_PKCS7,
        block_size: int = 16,
        encoding=UTF8
    ):
        self.key = key.encode(encoding)
        self.iv = iv and iv.encode(encoding) or None
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

    def encrypt_ecb(self, text: str) -> str:
        # 字符串补位
        text = self.pad_func(text, self.block_size)
        cipher = AES.new(self.key, AES.MODE_ECB)
        # 加密
        result = cipher.encrypt(text.encode(self.encoding))
        # 将密文使用Base64进行编码后转为字符串类型
        return b64encode(result).decode(self.encoding)

    def decrypt_ecb(self, content: str) -> str:
        # 实例化aes
        cipher = AES.new(self.key, AES.MODE_ECB)
        # 解密
        data = cipher.decrypt(b64decode(content)).decode(self.encoding)
        # 清除填充
        return self.unpad_func(data)

    def encrypt_cbc(self, text: str) -> str:
        # 字符串补位
        text = self.pad_func(text, self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 加密
        result = cipher.encrypt(text.encode(self.encoding))
        # 将密文使用Base64进行编码后转为字符串类型
        return b64encode(result).decode(self.encoding)

    def decrypt_cbc(self, content: str) -> str:
        # 实例化aes
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 解密
        data = cipher.decrypt(b64decode(content)).decode(self.encoding)
        # 清除填充
        return self.unpad_func(data)


class EncryptRSA(object):
    key_compile = compile(r'^(-----[a-zA-Z\s]+-----)\n*([a-zA-Z\d\n\+\=\/]+)\n*(-----[a-zA-Z\s]+-----)$')

    def __init__(self, cipher) -> None:
        self.cipher = cipher

    @classmethod
    def format_key(cls, rsa_key: str):
        """
        格式化rsa_key
        如果是pem格式的key则添加换行符
        """
        if not rsa_key.startswith("-----"):
            return rsa_key
        match_result = cls.key_compile.match(rsa_key)
        if match_result is None:
            return rsa_key
        return "\n".join(match_result.groups())

    def b64_encrypt(self, text: str, encoding: str = UTF8) -> str:
        """
        加密后返回base64
        """
        cipher_content = self.cipher.encrypt(text.encode(encoding))
        return b64encode(cipher_content).decode(encoding)

    def b64_decrypt(self, cipher_text: str, encoding: str = UTF8) -> Union[str, None]:
        """
        解密base64密文
        """
        content = self.cipher.decrypt(cipher_text.encode(encoding), None)
        return content and b64decode(content) or None

    def hex_encrypt(self, text: str, encoding: str = UTF8) -> str:
        """
        加密后返回16进制字符串
        """
        cipher_content = self.cipher.encrypt(text.encode(encoding))
        return b2a_hex(cipher_content).decode(encoding)

    def hex_decrypt(self, cipher_text: str, encoding: str = UTF8) -> Union[str, None]:
        """
        解密16进制密文
        """
        content = self.cipher.decrypt(cipher_text.encode(encoding), None)
        return content and a2b_hex(content).decode(encoding) or None

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
    rsa_key = "-----BEGIN PUBLIC KEY-----MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5gsH+AA4XWONB5TDcUd+xCz7ejOFHZKlcZDx+pF1i7Gsvi1vjyJoQhRtRSn950x498VUkx7rUxg1/ScBVfrRxQOZ8xFBye3pjAzfb22+RCuYApSVpJ3OO3KsEuKExftz9oFBv3ejxPlYc5yq7YiBO8XlTnQN0Sa4R4qhPO3I2MQIDAQAB-----END PUBLIC KEY-----"
    pubkey_rsa = EncryptRSA.from_key(rsa_key)
    print(pubkey_rsa.b64_encrypt("1234456"))
    modules = "00C1E3934D1614465B33053E7F48EE4EC87B14B95EF88947713D25EECBFF7E74C7977D02DC1D9451F79DD5D1C10C29ACB6A9B4D6FB7D0A0279B6719E1772565F09AF627715919221AEF91899CAE08C0D686D748B20A3603BE2318CA6BC2B59706592A9219D0BF05C9F65023A21D2330807252AE0066D59CEEFA5F2748EA80BAB81"
    e = "10001"
    pubkey_rsa1 = EncryptRSA.from_construct((int(modules, base=16), int(e, base=16)))
    print(pubkey_rsa1.hex_encrypt("598af7e714e274b5"))
