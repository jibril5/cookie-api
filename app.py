from flask import Flask, Response, request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import tempfile
import shutil
import time
import os

app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "une-cle-secrete")

PAGE_1 = os.getenv("PAGE_1", "https://5afterdark.mom/")
PAGE_2 = os.getenv("PAGE_2", "https://5afterdark.mom/video/7e4de128-b10f-dc2b-0542-7590c441630e")
COOKIE_NAME = os.getenv("COOKIE_NAME", "__illit")

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")


def text_response(text, status=200):
    res = Response(text, status=status, mimetype="text/plain")
    res.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    res.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    res.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return res


@app.route("/")
def home():
    return text_response("Serveur OK")
    
@app.route("/test-chrome")
def test_chrome():
    user_data_dir = tempfile.mkdtemp(prefix="chrome-user-data-")
    driver = None

    try:
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"

        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://example.com")
        return text_response(driver.title)

    except Exception as e:
        return text_response(str(e), status=500)

    finally:
        if driver:
            driver.quit()

        shutil.rmtree(user_data_dir, ignore_errors=True)

@app.route("/debug")
def debug():
    try:
        chromium_version = subprocess.check_output(
            ["/usr/bin/chromium", "--version"],
            text=True
        ).strip()
    except Exception as e:
        chromium_version = f"Erreur chromium: {e}"

    try:
        driver_version = subprocess.check_output(
            ["/usr/bin/chromedriver", "--version"],
            text=True
        ).strip()
    except Exception as e:
        driver_version = f"Erreur chromedriver: {e}"

    return text_response(
        f"Chromium: {chromium_version}\nChromeDriver: {driver_version}"
    )


@app.route("/cookie", methods=["GET", "OPTIONS"])
def get_cookie():
    if request.method == "OPTIONS":
        return text_response("")

    key = request.args.get("key")

    if key != SECRET_KEY:
        return text_response("Unauthorized", status=401)

    user_data_dir = tempfile.mkdtemp(prefix="chrome-user-data-")
    driver = None

    try:
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

        service = Service("/usr/bin/chromedriver")

        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(PAGE_1)
        time.sleep(1)

        driver.get(PAGE_2)
        time.sleep(2)

        cookies = driver.get_cookies()

        for cookie in cookies:
            if cookie.get("name") == COOKIE_NAME:
                return text_response(cookie.get("value", ""))

        return text_response("Cookie introuvable", status=404)

    except Exception as e:
        return text_response(str(e), status=500)

    finally:
        if driver:
            driver.quit()

        shutil.rmtree(user_data_dir, ignore_errors=True)
