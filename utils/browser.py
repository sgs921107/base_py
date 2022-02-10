#!/usr/bin/env python
# -*- coding=utf8 -*-
'''
Author: xiangcai
Date: 2021-11-27 11:16:59
LastEditors: xiangcai
LastEditTime: 2022-02-10 19:19:32
Description: file content
'''
from typing import Dict, Any, List

from pyppeteer import browser
from pyppeteer.browser import Browser
from pyppeteer.launcher import Launcher
from pyppeteer.element_handle import ElementHandle
from selenium.webdriver.common.by import By
# from selenium.webdriver import Chrome, ChromeOptions
from seleniumwire.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from common import config, logger


class AsyncChromeBrowser(Browser):
    _page = None

    async def page(self):
        if self._page is None:
            self._page = (await self.pages())[0]
        return self._page

    async def goto(self, url, new_page: bool = False):
        if new_page:
            self._page = await self.browser.newPage()
        page = await self.page()
        await page.evaluateOnNewDocument(
            '''
            () => {
                Object.defineProperty(
                    navigator,
                    'webdriver',
                    {get: () => undefined}
                )
            }
            '''
        )
        await page.goto(url)

    async def screenshot(self, options: Dict[str, Any] = None, **kwargs: Any):
        page = await self.page()
        await page.screenshot(options, **kwargs)

    async def find_elements_by_selector(self, expression: str) -> ElementHandle:
        page = await self.page()
        return await page.JJ(expression)

    async def find_element_by_selector(self, expression: str) -> ElementHandle:
        page = await self.page()
        return await page.J(expression)

    async def find_elements_by_xpath(self, expression: str) -> List[ElementHandle]:
        page = await self.page()
        return await page.Jx(expression)

    async def find_element_by_xpath(self, expression: str) -> ElementHandle:
        elements = await self.find_elements_by_xpath(expression)
        return elements and elements[0] or None

    async def WaitForXpath(
        self,
        expression: str,
        options: Dict[str, Any] = None,
        **kwargs: Any
    ):
        page = await self.page()
        await page.waitForXPath(expression, options, **kwargs)

    async def waitForNavigation(self, options: Dict[str, Any] = None, **kwargs: Any):
        page = await self.page()
        return await page.waitForNavigation(options, **kwargs)

    async def executeJS(self, js: str, *args: Any, force_expr: bool = False):
        page = await self.page()
        await page.evaluate(js, *args, force_expr)

    async def set_user_agent(self, user_agent: str) -> None:
        page = await self.page()
        await page.setUserAgent(user_agent)


browser.Browser = AsyncChromeBrowser


class AsyncLauncher(Launcher):

    def __init__(self, options: Dict[str, Any] = None, **kwargs: Any) -> None:
        super().__init__(options=options, **kwargs)
        self.browsers: List[AsyncChromeBrowser] = list()

    async def create_browser(self) -> AsyncChromeBrowser:
        browser = await self.launch()
        self.browsers.append(browser)
        return browser

    async def __aenter__(self):
        return self.get_instance()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error("%s: %s\r\n%s" % (exc_type, exc_val, exc_tb))
        await self.close()

    async def close(self) -> None:
        for b in self.browsers:
            await b.close()

    @classmethod
    def get_instance(cls):
        return cls(
            headless=config.browser_headless,
            logLevel="INFO",
            # 移除自动化测试控制的提示
            args=[
                "--incognito",
                "--disable-gpu",
                "--disable-infobars",
                f"--window-size={config.browser_width},{config.browser_height}"
            ],
            defaultViewport={'width': config.browser_width, 'height': config.browser_height},
        )


class ChromeBrowser(Chrome):
    DEFAULT_TIMEOUT = 20

    def wait_element_located(
        self,
        expression: str,
        by: str = By.XPATH,
        timeout: float = DEFAULT_TIMEOUT,
        **kwargs
    ) -> WebElement:
        """
        等待标签加载完毕
        param expression: 表达式
        by: 表达式类型
        return: 标签
        """
        return WebDriverWait(
            self,
            timeout,
            **kwargs
        ).until(EC.presence_of_element_located((by, expression)))

    def wait_element_clickable(
            self,
            expression: str,
            by: str = By.XPATH,
            timeout: float = DEFAULT_TIMEOUT,
            **kwargs
    ) -> WebElement:
        """
        等待标签可点击
        """
        return WebDriverWait(
            self,
            timeout,
            **kwargs
        ).until(EC.element_to_be_clickable((by, expression)))

    def __enter__(self):
        return self.get_instance()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error("%s: %s\r\n%s" % (exc_type, exc_val, exc_tb))
        self.quit()

    @classmethod
    def get_instance(cls, driver_path: str = "chromedriver", proxy=None):
        driver_options = ChromeOptions()
        # 设置语言编码
        driver_options.add_argument("lang=zh_CN.UTF-8")
        # 隐身模式
        driver_options.add_argument("--incognito")
        # 设置窗口大小
        driver_options.add_argument(f"--window-size={config.browser_width},{config.browser_height}")
        # 禁止使用gpu加速   谷歌文档提到需要加上这个属性来规避bug
        driver_options.add_argument("--disable-gpu")
        # 允许超级权限运行行用户运行
        driver_options.add_argument("--no-sandbox")
        # driver_options.add_argument("--disable-dev-shm-usage")
        # 移除自动化测试控制的提示
        # driver_options.add_argument("--disable-infobars")
        driver_options.add_experimental_option("useAutomationExtension", False)
        driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if config.browser_headless:
            driver_options.add_argument("--headless")
        # 添加代理
        seleniumwire_options = dict()
        if proxy:
            seleniumwire_options = {
                'proxy': proxy
            }
        browser = cls(
            executable_path=driver_path,
            options=driver_options,
            seleniumwire_options=seleniumwire_options
        )
        # 防检测
        browser.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(
                        navigator,
                        'webdriver',
                        {get: () => undefined}
                    )
                """
            }
        )
        return browser
