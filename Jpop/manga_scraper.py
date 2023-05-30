import httpx
from selectolax.parser import HTMLParser
from dataclasses import asdict, dataclass
from os import path, makedirs
import logging
from csv import DictWriter

# record general informations
logging.basicConfig(
        level=logging.INFO,
        filename="web_scraper.log",
        format="%(asctime)s - %(message)s",
        datefmt="%d-%b-%y %H%M"
        )

# Data container
@dataclass
class Manga:
    title: str
    price: str
    cover: str

# Make a directory to store data
def make_directory(directory):
    if not path.exists(directory):
        logging.info(f"Making directory: {directory}")
        makedirs(directory)
    else:
        logging.info(f"{directory} alredy exists")

# Make a request and get response
def get_http_request(page):
    url = f"https://j-pop.it/it/catalog/category/view/id/696/s/fumetti/?p={page}?product_list_dir=asc&product_list_order=name"
    headers = {
                "User-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36" 
                }

    response = httpx.get(url, headers=headers)

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logging.info(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
    except httpx.RequestError as exc:
        logging.info(f"An error occurred while requesting {exc.request.url!r}.")
    return response

def get_html_text(starting_page):
    r = get_http_request(starting_page)
    # Parse raw HTML 
    return HTMLParser(r.text)

# Data parser
def product_info(html):
    info = []
    products = html.css("li.item.product.product-item")
    
    for product in products:
        p = Manga(
                title=product.css_first("a.product-item-link").text().strip(),
                price=product.css_first("span.price").text().replace("\xa0€", '€'),
                cover=product.css_first("img.img-fluid.product-image-photo").attributes["src"]
            )
        info.append(asdict(p))
    return info

# Make csv file
def make_csv(product):
    try:
        with open("products.csv", "a") as f:
            wr = DictWriter(f, fieldnames=["title", "price", "cover"])
            wr.writerows(product)
            logging.info("csv file successfully created")
    except OSError as e:
        logging.info(f"File already exists. Error {e}")

def main():
    # Loop over pages to extract data
    for i in range(1, 5):
        html = get_html_text(i)
        res = product_info(html)
        make_csv(res)

# Main driver
if __name__ == "__main__":
    # print(get_http_request(1))
    # print(get_html_text(1))
    main()


