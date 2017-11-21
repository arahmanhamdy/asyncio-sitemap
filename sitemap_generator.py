#!/usr/bin/env python
import time
import argparse
import aiohttp
import asyncio
import async_timeout
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from lxml import etree


class SitemapGenerator:
    """
    The base class for sitemap generator
    """

    def __init__(self, base_url, max_parallel_tasks=None, output=None):
        """
        :param base_url:str: the base url to start crawling
        :param max_parallel_tasks:int: max asyncio parallel tasks
        :param output:str: the output file for the sitemap
        """
        self.base_url = base_url
        if not max_parallel_tasks:
            max_parallel_tasks = 5
        self.max_parallel_tasks = max_parallel_tasks
        self.visited_urls = set()
        self.async_loop = asyncio.get_event_loop()
        self.urls_queue = asyncio.Queue(loop=self.async_loop)
        self.output = output

        # add base url to urls_queue as a starting point
        self.urls_queue.put_nowait(self.base_url)

    def is_valid_url(self, url):
        if '#' in url:
            url = url[:url.find('#')]
        if url in self.visited_urls:
            return False
        if self.base_url not in url:
            return False
        return True

    async def get_html(self, url):
        async with aiohttp.ClientSession(loop=self.async_loop) as sess:
            with async_timeout.timeout(10):
                async with sess.get(url) as response:
                    return await response.text()

    async def process(self):
        while True:
            url = await self.urls_queue.get()
            if self.is_valid_url(url):
                self.visited_urls.add(url)
                html = await self.get_html(url)
                parsed_html = BeautifulSoup(html, "html.parser")
                for link in parsed_html.find_all('a', href=True):
                    new_url = urljoin(self.base_url, link['href'])
                    # remove trailing slash
                    new_url = new_url.rstrip("/")
                    if self.is_valid_url(new_url):
                        self.urls_queue.put_nowait(new_url)
            self.urls_queue.task_done()

    async def start_crawl(self):
        tasks = [asyncio.ensure_future(self.process(), loop=self.async_loop)
                 for _ in range(self.max_parallel_tasks)]
        await self.urls_queue.join()
        for t in tasks:
            t.cancel()

    def create_xml(self):
        namespace_map = {
            None: "http://www.sitemaps.org/schemas/sitemap/0.9",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        }
        root = etree.Element('urlset', nsmap=namespace_map)

        for url in self.visited_urls:
            url_node = etree.Element('url')
            loc_node = etree.Element('loc')
            loc_node.text = url
            url_node.append(loc_node)
            root.append(url_node)

        if self.output:
            etree.ElementTree(root).write(self.output, xml_declaration=True, encoding='utf-8', pretty_print=True)
        else:
            print(etree.tostring(root, encoding='utf-8', pretty_print=True))

    def generate_sitemap(self):
        t1 = time.time()
        self.async_loop.run_until_complete(self.start_crawl())
        self.create_xml()
        t2 = time.time() - t1
        msg = "Sitemap Generated for {url} in {time} seconds with {count} URLs "
        print(msg.format(url=self.base_url, time=t2, count=len(self.visited_urls)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Base URL to generate sitemap")
    parser.add_argument("-n", "--num", help="Number of parallel tasks", type=int)
    parser.add_argument("-o", "--output",
                        help="output sitemap file, if ommited the sitemap will be printed on stdout")
    args = parser.parse_args()
    parsed_url = urlparse(args.url)
    if parsed_url.scheme and parsed_url.netloc:
        gen = SitemapGenerator(args.url, args.num, args.output)
        gen.generate_sitemap()
    else:
        print("URL is not valid, please enter a valid one i.e: http://centione.com")
        exit(1)
