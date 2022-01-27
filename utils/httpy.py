#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: httpx的扩展
'''
import typing
from typing import Union

import httpx
import httpcore
from async_retrying import retry
from httpx._utils import URLPattern
from scrapy.exceptions import NotSupported
from httpx._types import VerifyTypes, CertTypes
from httpx._config import DEFAULT_LIMITS, Limits
from scrapy.selector import Selector, SelectorList

from common import logger, config
from common.conts import DEFAULT_HEADERS


class Response(httpx._client.Response):
    """
    扩展httpx的Response
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._selector = None

    @property
    def selector(self) -> Selector:
        if self._selector is None:
            try:
                self._selector = Selector(text=self.text)
            except Exception as e:
                logger.exception("Response Type Error: %s" % e)
                self._selector = False
        return self._selector

    def xpath(self, query=None, namespaces=None, **kwargs) -> SelectorList:
        if not self.selector:
            raise NotSupported("Response content isn't text")
        return self.selector.xpath(query, namespaces, **kwargs)


httpx._client.Response = Response


class HttpClient(httpx.AsyncClient):
    """
    扩展httpx的客户端, 方便更换代理
    """
    default_headers = DEFAULT_HEADERS.copy()

    def __init__(self, **kwargs):
        headers = DEFAULT_HEADERS.copy()
        headers.update(kwargs.get("headers") or dict())
        kwargs["headers"] = headers
        super().__init__(**kwargs)

    async def close_proxies(self):
        """
        移除代理
        """
        for proxy in self._proxies.values():
            if proxy is not None:
                await proxy.aclose()
        self._proxies = dict()

    async def reset_proxies(
        self,
        proxies,
        *,
        verify: VerifyTypes = True,
        cert: CertTypes = None,
        http2: bool = False,
        limits: Limits = DEFAULT_LIMITS,
        transport: httpcore.AsyncHTTPTransport = None,
        app: typing.Callable = None,
        trust_env: bool = True,
    ):
        """
        重设客户端代理
        """
        await self.close_proxies()
        allow_env_proxies = trust_env and app is None and transport is None
        proxy_map = self._get_proxy_map(proxies, allow_env_proxies)
        self._proxies: typing.Dict[
            URLPattern, typing.Optional[httpcore.AsyncHTTPTransport]
        ] = {
            URLPattern(key): None
            if proxy is None
            else self._init_proxy_transport(
                proxy,
                verify=verify,
                cert=cert,
                http2=http2,
                limits=limits,
                trust_env=trust_env,
            )
            for key, proxy in proxy_map.items()
        }
        self._proxies = dict(sorted(self._proxies.items()))

    @retry(fallback=None)
    async def send_req(
        self,
        url,
        method="GET",
        timeout=config.srv_timeout,
        session=True,
        proxies=None,
        meta=None,
        **kwargs
    ) -> Union[Response, None]:
        """
        发送一个请求
        """
        try:
            if session:
                await self.reset_proxies(proxies)
                resp = await self.request(method, url, timeout=timeout, **kwargs)
            else:
                async with httpx.AsyncClient(headers=self.default_headers) as cli:
                    resp = await cli.request(method, url, timeout=timeout, **kwargs)
        except Exception as e:
            logger.error("Request Failed: %s, url: %s" % (e, url))
            raise
        resp.meta = meta
        return resp
