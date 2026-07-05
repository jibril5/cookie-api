from flask import Flask, Response, request
from playwright.sync_api import sync_playwright
import os
import time

app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "une-cle-secrete")

PAGE_1 = os.getenv("PAGE_1", "https://5afterdark.mom/")
PAGE_2 = os.getenv(
    "PAGE_2",
    "https://5afterdark.mom/video/7e4de128-b10f-dc2b-0542-7590c441630e"
)

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


@app.route("/debug")
def debug():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()
            page.goto(
                "https://example.com",
                wait_until="domcontentloaded",
                timeout=30000
            )

            title = page.title()
            browser.close()

        return text_response(f"Playwright OK\nTitle: {title}")

    except Exception as e:
        return text_response(str(e), status=500)


@app.route("/cookie", methods=["GET", "OPTIONS"])
def get_cookie():
    if request.method == "OPTIONS":
        return text_response("")

    key = request.args.get("key")
    if key != SECRET_KEY:
        return text_response("Unauthorized", status=401)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage"
                ]
            )

            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )

            page = context.new_page()

            page.goto(PAGE_1, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            page.goto(PAGE_2, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            cookies = context.cookies()

            for cookie in cookies:
                if cookie.get("name") == COOKIE_NAME:
                    value = cookie.get("value", "")
                    browser.close()
                    return text_response(value)

            cookie_names = [cookie.get("name", "") for cookie in cookies]

            browser.close()

            return text_response(
                "Cookie introuvable\nCookies trouvés : " + ", ".join(cookie_names),
                status=404
            )

    except Exception as e:
        return text_response(str(e), status=500)
