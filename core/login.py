import time
import json
import os


def save_cookies(driver, cookie_file="data/session_cookies.json"):
    """
    Opens HappyMail login page and waits for manual login.
    Saves session cookies to a file.
    """
    print("🔐 Please log in manually (you have 60 seconds)...")
    driver.get("https://happymail.co.jp/login/?Log=newspi")
    time.sleep(60)  # You log in manually during this wait

    cookies = driver.get_cookies()
    os.makedirs(os.path.dirname(cookie_file), exist_ok=True)

    with open(cookie_file, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)

    print(f"✅ Cookies saved to {cookie_file}")


def login_with_cookies(driver, cookie_file="data/session_cookies.json"):
    """
    Loads cookies and attempts login with them, safely.
    """
    print("🔁 Attempting login using saved cookies...")

    if not os.path.exists(cookie_file):
        raise FileNotFoundError(f"Cookie file not found: {cookie_file}")

    # 1. Load neutral page first (MUST be the same domain!)
    driver.get("https://happymail.co.jp/")
    time.sleep(2)

    # 2. Load and inject cookies
    with open(cookie_file, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    for cookie in cookies:
        if "sameSite" in cookie:
            del cookie["sameSite"]
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"⚠️ Failed to add cookie: {cookie.get('name', '')} → {e}")

    # 3. Now go to target page
    driver.get("https://happymail.co.jp/app/html/message_list.php")
    time.sleep(3)

    # # 4. Optional: detect if still on login page
    # if "login" in driver.current_url or "ログイン" in driver.page_source:
    #     print("❌ Login via cookies failed — possibly expired session.")
    # else:
    #     print("✅ Logged in using cookies.")