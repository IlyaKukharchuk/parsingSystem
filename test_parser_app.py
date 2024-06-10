import pytest
from bs4 import BeautifulSoup
from scrapers import parse_category, parse_category_async
from main import get_url

# pytest test_parser_app.py

@pytest.fixture(scope="module")
def category_url():
    return get_url()  # Ensure get_url() provides a valid category URL for testing

def test_parse_category(category_url):
    products = parse_category(category_url)
    assert isinstance(products, list)
    assert all('name' in product and 'price' in product for product in products)

@pytest.mark.asyncio
async def test_parse_category_async(category_url):
    products = await parse_category_async(category_url)
    assert isinstance(products, list)
    assert all('name' in product and 'price' in product for product in products)

def test_parse_category_invalid_url():
    with pytest.raises(Exception) as excinfo:
        parse_category("https://invalid-url.com")
    assert "Error fetching data" in str(excinfo.value)

@pytest.mark.asyncio
async def test_parse_category_async_invalid_url():
    with pytest.raises(Exception) as excinfo:
        await parse_category_async("https://invalid-url.com")
    assert "Error fetching data" in str(excinfo.value)

def test_parse_category_structure():
    html_content = '''
    <div class="ProductCard_product__3t2Ve">
        <a class="ProductCard_productName__jWFZE">Test Product</a>
        <div class="ProductCard_productPrice__Jt7Xf">$10</div>
    </div>
    <div class="ProductCard_product__3t2Ve">
        <a class="ProductCard_productName__jWFZE">Another Product</a>
        <div class="ProductCard_productPrice__Jt7Xf">$20</div>
    </div>
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    for product_element in soup.find_all('div', class_='ProductCard_product__3t2Ve'):
        name = product_element.find('a', class_='ProductCard_productName__jWFZE').text.strip()
        price_element = product_element.find('div', class_='ProductCard_productPrice__Jt7Xf')
        price = price_element.text.strip() if price_element else None
        products.append({'name': name, 'price': price})

    assert len(products) == 2
    assert products[0]['name'] == 'Test Product'
    assert products[0]['price'] == '$10'
    assert products[1]['name'] == 'Another Product'
    assert products[1]['price'] == '$20'

@pytest.mark.asyncio
async def test_parse_category_async_structure():
    html_content = '''
    <div class="ProductCard_product__3t2Ve">
        <a class="ProductCard_productName__jWFZE">Test Product</a>
        <div class="ProductCard_productPrice__Jt7Xf">$10</div>
    </div>
    <div class="ProductCard_product__3t2Ve">
        <a class="ProductCard_productName__jWFZE">Another Product</a>
        <div class="ProductCard_productPrice__Jt7Xf">$20</div>
    </div>
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    for product_element in soup.find_all('div', class_='ProductCard_product__3t2Ve'):
        name = product_element.find('a', class_='ProductCard_productName__jWFZE').text.strip()
        price_element = product_element.find('div', class_='ProductCard_productPrice__Jt7Xf')
        price = price_element.text.strip() if price_element else None
        products.append({'name': name, 'price': price})

    assert len(products) == 2
    assert products[0]['name'] == 'Test Product'
    assert products[0]['price'] == '$10'
    assert products[1]['name'] == 'Another Product'
    assert products[1]['price'] == '$20'
