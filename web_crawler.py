import json
import re
from os.path import basename, join, splitext, isfile

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}
URL = "https://www.musik-produktiv.de/e-gitarre/"

PATHS = {
    'store_attributes': ('guitar_attributes', '.txt'),
    'store_description': ('guitar_description', '.txt'),
    'store_reviews': ('guitar_reviews', '.json'),
    'download_image': ('guitar_images', '.jpg')
}


def run():
    num_pages = get_num_pages(load_page(URL))
    for index in range(0, num_pages):
        if num_pages == 0:
            url = URL
        else:
            url = URL + f'?p={index}'

        print(f"Processing page: {index}")
        download_page(url)


def download_page(url: str):
    guitar_urls = get_guitar_urls(url)
    for g_url in tqdm(guitar_urls):
        try:
            store_data(g_url)
        except Exception as error:
            print(f"Error with url: {g_url}")
            print(error)


def get_guitar_urls(url: str) -> list:
    soup = load_page(url)
    grid = soup.find("ul", class_="artgrid clearfix col-4")
    guitar_urls = [x.a['href'] for x in grid.find_all("li")]
    return guitar_urls


def load_page(url):
    page = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def get_num_pages(soup: BeautifulSoup) -> int:
    return int(soup.find("div", class_="list_page").find_all("a")[-1].text)


def store_data(g_url: str):
    data_id = get_id(g_url)
    tmp_page = requests.get(g_url, data_id, headers=HEADERS)
    tmp_page = BeautifulSoup(tmp_page.content, 'html.parser')
    image_url = tmp_page.find(id="zoom")['href']
    download_image(image_url, data_id, HEADERS)
    store_attributes(tmp_page, data_id)
    store_reviews(tmp_page, data_id)
    store_description(tmp_page, data_id)


def add_folder_and_only_run_if_no_file(func):
    def wrapper(*args, **kwargs):
        # data_id is always the second argument
        data_id = args[1]
        folder, ext = PATHS[func.__name__]
        filepath = join(folder, data_id + ext)
        if isfile(filepath):
            return
        else:
            return func(*args, folder=folder, ext=ext, **kwargs)

    return wrapper


@add_folder_and_only_run_if_no_file
def download_image(guitar_url: str, data_id: str, headers: dict, **kwargs):
    ext = splitext(basename(guitar_url))[-1]
    filepath = join(kwargs["folder"], data_id + ext)

    img_data = requests.get(url=guitar_url, headers=headers).content
    with open(filepath, 'wb') as handler:
        handler.write(img_data)


@add_folder_and_only_run_if_no_file
def store_attributes(page: BeautifulSoup, data_id: str, **kwargs):
    attribute_list = page.find("ul", class_="eigenschaften")
    attributes = [x.text for x in attribute_list.find_all("li")]
    filepath = join(kwargs["folder"], data_id + kwargs["ext"])
    with open(filepath, 'w') as file:
        [file.write(x + '\n') for x in attributes]


@add_folder_and_only_run_if_no_file
def store_description(page: BeautifulSoup, data_id: str, **kwargs):
    description = page.find("div", class_="product-description")
    filepath = join(kwargs["folder"], data_id + kwargs["ext"])
    with open(filepath, 'w') as file:
        file.write(description.text)


@add_folder_and_only_run_if_no_file
def store_reviews(page: BeautifulSoup, data_id: str, **kwargs):
    reviews = page.find_all("div", class_="review")
    out = [read_review(x) for x in reviews]
    with open(join(kwargs["folder"], data_id + kwargs["ext"]), 'w') as file:
        json.dump(out, file)


def get_id(g_url: str) -> str:
    return g_url.split('/')[-1].replace(".html", "")


def read_review(rev_item: BeautifulSoup) -> dict:
    out = {}
    rgx = 'width: (\d+)%'
    _, keys_, title, user, text, _ = rev_item.text.split('\n')

    out.update({
        "title": title,
        "text": text
    })

    stars_ = rev_item.find_all("span", class_="mp-stars")
    # "width: 100%" -> 100 -> 100/20 -> 5 stars
    keys_ = [x for x in keys_.split(" ") if x != ""]
    assert len(keys_) == len(stars_)
    for key, star in zip(keys_, stars_):
        num_stars = int(
            re.match(rgx, star.find("span")['style']).group(1)) / 20
        out[key] = num_stars

    return out


if __name__ == '__main__':
    run()
