import os
import wget
import glob
import argparse
import urllib.request
from urllib.request import urlopen as request
from bs4 import BeautifulSoup, SoupStrainer

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def headless_visitor(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.get(url)
    return browser.page_source

def build_link_filter(soup):
    results = soup.find_all(lambda tag: tag.name == "a" and "href" in tag.attrs and "class" in tag.attrs)
    classes = list(set([ " ".join(r.attrs["class"]) for r in results if "dig-Link" in r.attrs["class"]]))
    try:
        print("Is this your class? " + classes[0])
    
    except IndexError:
        print("No links found :(")
        exit(0)
    return SoupStrainer("a", attrs={"class" : classes[0]})


def download_links(links):

    for l in set(links):

        fname = l.split("?")[0].split("/")[-1]
        if os.path.exists(fname):
            print(f"Skipping download of {fname}, as it already exists...")
            continue
        print(f"Downloading {fname} from {l}")
        wget.download(l, fname)


def main(url=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        nargs="?",
        type=str,
        default=None,
        help="Optional url"
    )
    args = parser.parse_args()

    if not url:
        url = args.url

    if not url:
        url = input("Url to reads: ")
    html = headless_visitor(url)

    first_supper = BeautifulSoup(html, 'html.parser')
    only_links = build_link_filter(first_supper)

    second_supper = BeautifulSoup(html, 'html.parser', parse_only=only_links)
    links = [a.attrs["href"].replace("&dl=0","&dl=1") for a in second_supper if a.attrs["href"]]

    print(links)

    if len(links) < 10:
        raise Exception(f"I don\'t think these are your samples, bud...\nI got: {' '.join(links)}")
    else:
        download_links(links)


if __name__ == "__main__":
    main()
