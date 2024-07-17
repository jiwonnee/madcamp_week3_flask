from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # 모든 경로에 대해 CORS 허용

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"
    }
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()  # 웹페이지의 상태가 정상인지 확인
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({"error": "Request failed", "message": str(e)}), 500

    soup = BeautifulSoup(res.text, "lxml")  # 가져온 HTML 문서를 파서를 통해 BeautifulSoup 객체로 만듦

    # class가 "prod-buy-header"인 div 태그를 찾는다
    product_header_div = soup.find("div", class_="prod-buy-header")
    if product_header_div:
        # 해당 div 태그 내의 "prod-buy-header__title" 클래스가 있는 h1 태그를 찾는다
        product_name = product_header_div.find("h1", class_="prod-buy-header__title").get_text(strip=True)
    else:
        product_name = "No product name found"

    # class가 "total-price"인 span 태그를 찾는다
    product_price_span = soup.find("span", class_="total-price")
    if product_price_span:
        product_price = product_price_span.find("strong").get_text(strip=True)
    else:
        product_price = "No product price found"

    # class가 "prod-image__detail"인 img 태그 안의 이미지 URL을 찾는다
    image_tag = soup.find("img", class_="prod-image__detail")
    if image_tag:
        image_url = "https:" + image_tag.get("src")
    else:
        image_url = "No image found"

    # 디버깅 출력을 추가하여 데이터가 제대로 크롤링되는지 확인
    print(f"Product Name: {product_name}")
    print(f"Product Price: {product_price}")
    print(f"Image URL: {image_url}")

    return jsonify({"product_name": product_name, "product_price": product_price, "image_url": image_url})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
