from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import requests
import csv
import json

BASE_URL = "https://www.villanovo.com"

def check_pagination():
    return False

def get_villas_by_city(city: str):
    villas = set()
    page = 1

    print(f"Start - Parse the city ::: {city}")

    while True:
        url = city + f"?page={page}"

        print(f"-> Checking page {page} ::: {url}")

        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        if "Page not found" in soup.text: 
            print(f"Page not found for URL {url}")
            break

        urls = [
            BASE_URL + item.attrs["href"] 
            for item in soup.select("div.row.villas > div.is-sort > div.villa > div.villa-img > a:first-child")
        ]
        villas.update(urls)

        page = page + 1

    print(f"Found {len(villas)} villas")

    print(f"End - Parse the city ::: {city}")

    return villas



def parse():
    soup = BeautifulSoup(requests.get(BASE_URL).content, "html.parser")

    cities = [BASE_URL + city.attrs["href"] for city in soup.select("div.cities > a")]

    list_of_villas = set()

    for city in cities:
        villas = get_villas_by_city(city)
        list_of_villas.update(villas)

    print()

    



if __name__ == "__main__":
    parse()


print("Done!")