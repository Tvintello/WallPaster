from parsers.parser import Parser
from bs4 import BeautifulSoup
import requests
import math
from random import random


class WallsCloud(Parser):
    url = "https://wallscloud.net/ru/search"
    name = "WallsCloud"

    def get_available_resolutions(self, link):
        req = requests.get(link)
        soup = BeautifulSoup(req.text, "html.parser")
        block = soup.find("div", class_="resblocks")
        resolutions = [list(map(int, i.text.split(" x "))) for i in block.find_all("a", recursive=True)]
        return resolutions

    def get_image_bytes(self, link: str, resolution: list):
        ref_download = f"{link}/{resolution[0]}x{resolution[1]}/download"
        byte = requests.get(ref_download).content

        return byte

    def get_image_links(self, query: dict):
        pages = self.get_pages(query)
        images = []

        query["page"] = round(random() * pages + 1)
        soup = BeautifulSoup(requests.get(self.url, params=query).content, "html.parser")
        block = soup.find('div', class_="grid-row walls_data")
        print(query)

        if block.find("figure"):
            for j in block.find_all("a", class_="wall_link"):
                images.append(j["href"])

        print(images)

        return images

    def get_pages(self, query: dict):
        pages = math.ceil(self.get_quantity(query) / 35)
        print("pages:", pages)
        return pages

    def get_quantity(self, query: dict):
        res = requests.get(self.url, params=query)
        soup = BeautifulSoup(res.text, 'html.parser')
        page_title = soup.find('div', class_='page-title')
        pictures = page_title.find('small').text
        pictures = int(pictures.split()[0])
        return pictures


