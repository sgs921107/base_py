#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Description: rabbitmq
'''

import asyncio
from typing import Union

from yarl import URL
from pamqp import specification as spec
from aio_pika.exceptions import ChannelClosed
from aio_pika import RobustConnection, RobustChannel, Message
from aiormq.types import ConsumerCallback, ArgumentsType, TimeoutType

from common import config, logger


class AChannel(RobustChannel):

    async def publish(
        self,
        message: Message,
        routing_key: str,
        *,
        mandatory: bool = True,
        immediate: bool = False,
        timeout: Union[int, float] = None
    ):
        if self.default_exchange is None:
            logger.error("PublishMessageFailed: channel not connected")
            return None
        return await self.default_exchange.channel.publish(
            message,
            routing_key,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout
        )

    async def basic_publish(
        self,
        body: bytes,
        *,
        exchange: str = "",
        routing_key: str = "",
        properties: spec.Basic.Properties = None,
        mandatory: bool = False,
        immediate: bool = False,
        timeout: TimeoutType = None
    ):
        if self.default_exchange is None:
            logger.error("PublishMessageFailed: channel not connected")
            return None
        return await self.default_exchange.channel.basic_publish(
            body,
            exchange=exchange,
            routing_key=routing_key,
            properties=properties,
            mandatory=mandatory,
            immediate=immediate,
            timeout=timeout
        )

    async def basic_consume(
        self,
        queue: str,
        consumer_callback: ConsumerCallback,
        *,
        no_ack: bool = False,
        exclusive: bool = False,
        arguments: ArgumentsType = None,
        consumer_tag: str = None,
        timeout: TimeoutType = None
    ):
        if self.default_exchange is None:
            logger.error("ConsumeMessageFailed: channel not connected")
            return None
        return await self.default_exchange.channel.basic_consume(
            queue,
            consumer_callback,
            no_ack=no_ack,
            exclusive=exclusive,
            arguments=arguments,
            consumer_tag=consumer_tag,
            timeout=timeout
        )

    async def basic_get(
        self,
        queue: str = "",
        no_ack: bool = False,
        timeout: TimeoutType = None
    ):
        if self.default_exchange is None:
            logger.error("ConsumeMessageFailed: channel not connected")
            return None
        return await self.default_exchange.channel.basic_get(
            queue,
            no_ack,
            timeout
        )

    async def ensure_queue(self, name: str):
        try:
            queue = await self.get_queue(name, ensure=True)
            return queue
        except ChannelClosed:
            logger.error("GetQueueFailed: queue %s not found" % name)
            await self.reopen()
            return None

    async def iter_queue(self, name: str, **kwargs):
        queue = await self.ensure_queue(name)
        if queue is None:
            return
        async with queue.iterator(**kwargs) as q:
            async for message in q:
                yield message


class ARabbitmq(RobustConnection):
    instance = None
    CHANNEL_CLASS = AChannel

    async def channel(
        self,
        channel_number: int = None,
        publisher_confirms: bool = True,
        on_return_raises=False,
        timeout: Union[int, float] = None
    ):
        if self.connection is None:
            await self.connect(
                timeout=self.kwargs.get("timeout"),
                client_properties=self.kwargs.get("client_properties"),
                loop=self.loop
            )
        channel = super().channel(channel_number, publisher_confirms, on_return_raises)
        if channel._channel is None:
            await channel.initialize(timeout)
        return channel

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            # query params
            kw = {
                "heartbeat": config.rabbitmq_heartbeat
            }
            # build url
            url = URL.build(
                scheme="amqp",
                host=config.rabbitmq_host,
                port=config.rabbitmq_port,
                user=config.rabbitmq_username,
                password=config.rabbitmq_password,
                # yarl >= 1.3.0 requires path beginning with slash
                path=(config.rabbitmq_vhost.startswith("/") and "" or "/") + config.rabbitmq_vhost,
                query=kw,
            )
            # instantiation rabbitmq connection
            cls.instance = cls(
                url=url,
                loop=asyncio.get_event_loop(),
            )
        return cls.instance


if __name__ == '__main__':
    pass
