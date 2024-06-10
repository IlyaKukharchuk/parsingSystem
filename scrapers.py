import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup

def parse_category(url):
    """Parses the given category URL and returns a list of product data dictionaries.

    Args:
        url (str): The URL of the category to parse.

    Returns:
        list: A list of dictionaries containing product data (name, price).

    Raises:
        Exception: If an error occurs during parsing.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product data using appropriate selectors based on life.com.by's structure
        products = []
        for product_element in soup.find_all('div', class_='ProductCard_product__3t2Ve'):  # Adjust selectors as needed
            name = product_element.find('a', class_='ProductCard_productName__jWFZE').text.strip()  # Adjust selectors
            price_element = product_element.find('div', class_='ProductCard_productPrice__Jt7Xf')  # Adjust selectors
            price = price_element.text.strip() if price_element else None

            products.append({'name': name, 'price': price})

        return products

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data from {url}: {e}")
    except Exception as e:
        raise Exception(f"Error parsing data from {url}: {e}")

async def parse_category_async(url):
    """Asynchronously parses the given category URL and returns a list of product data dictionaries.

    Args:
        url (str): The URL of the category to parse.

    Returns:
        list: A list of dictionaries containing product data (name, price).

    Raises:
        Exception: If an error occurs during parsing.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error fetching data from {url}: Status code {response.status}")

                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')

                # Extract product data using appropriate selectors based on life.com.by's structure
                products = []
                for product_element in soup.find_all('div', class_='ProductCard_product__3t2Ve'):  # Adjust selectors as needed
                    name = product_element.find('a', class_='ProductCard_productName__jWFZE').text.strip()  # Adjust selectors
                    price_element = product_element.find('div', class_='ProductCard_productPrice__Jt7Xf')  # Adjust selectors
                    price = price_element.text.strip() if price_element else None

                    products.append({'name': name, 'price': price})

                return products

    except aiohttp.ClientError as e:
        raise Exception(f"Error fetching data from {url}: {e}")
    except Exception as e:
        raise Exception(f"Error parsing data from {url}: {e}")
