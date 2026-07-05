from flask import Flask, Response, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "1234")

PAGE_1 = "https://5afterdark.mom/"
PAGE_2 = "https://5afterdark.mom/video/7e4de128-b10f-dc2b-0542-7590c441630e"
COOKIE_NAME = "__illit"


@app.route("/")
def home():
    return "Serveur OK"


@app.route("/cookie")
def get_cookie():
    key = request.args.get("key")

    if key != SECRET_KEY:
        return Response("Unauthorized", status=401)

    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")

    driver = None

    try:
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(PAGE_1)
        time.sleep(1)

        driver.get(PAGE_2)
        time.sleep(2)

        cookies = driver.get_cookies()

        for cookie in cookies:
            if cookie.get("name") == COOKIE_NAME:
                return Response(cookie.get("value", ""), mimetype="text/plain")

        return Response("Cookie introuvable", status=404, mimetype="text/plain")

    except Exception as e:
        return Response(str(e), status=500, mimetype="text/plain")

    finally:
        if driver:
            driver.quit()