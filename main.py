import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import load_json, append_to_csv

# === Load credentials ===
credentials = load_json("config/credentials.json")
email = credentials["email"]
password = credentials["password"]

# === Chrome Mobile Emulation Setup ===
mobile_emulation = { "deviceName": "iPhone SE" }
options = Options()
options.add_experimental_option("mobileEmulation", mobile_emulation)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--lang=ja-JP")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
driver.get("https://happymail.co.jp/sp/app/html/login.php")
time.sleep(3)

# === Login ===
print("🔐 Logging in...")
driver.find_element(By.NAME, "mailad").send_keys(email)
driver.find_element(By.NAME, "pswd").send_keys(password)
driver.find_element(By.NAME, "login").click()
time.sleep(3)

# === Go to 未返信 message page ===
driver.get("https://happymail.co.jp/sp/app/html/msglist.php?ad=0&jmode=3")
time.sleep(3)

# === Load tab_a settings ===
settings = load_json("config/tab_a_settings.json")
ng_words = settings["ng_words"]
ok_words = settings["required_keywords"]
message_templates = settings["messages"]["first"]
delay_sec = settings["delay_between_messages_sec"]

# === Load already messaged users from CSV ===
messaged_users = set()
csv_path = "output/messages_sent.csv"
if os.path.exists(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        for line in f.readlines()[1:]:  # skip header
            user = line.split(",")[0].strip()
            messaged_users.add(user)

# === Start message loop ===
threads = driver.find_elements(By.CSS_SELECTOR, "li.ds_user_post_link_item_r a")
print(f"📬 Found {len(threads)} messages")

for index, thread in enumerate(threads):
    # user_name = f"User{index}"  # Placeholder (we'll replace with real username in STEP 5)
    href = thread.get_attribute("href")
    if "uid=" in href:
        user_name = href.split("uid=")[-1].split("&")[0]  # Extract UID
    else:
        user_name = f"User{index}"  # fallback

    if user_name in messaged_users:
        print(f"⏭ Already messaged {user_name}, skipping.")
        continue

    try:
        print(f"➡ Opening message #{index+1} ({user_name})")
        thread.click()
        time.sleep(2)

        # Get message content
        message_text = driver.find_element(By.CLASS_NAME, "fs13px").text
        print("📝 Message:", message_text)

        # NG word check
        if any(ng in message_text for ng in ng_words):
            print("🚫 NG word found, skipping.")
            append_to_csv(csv_path, [user_name, "skipped_ng", message_text])
            driver.back()
            time.sleep(1)
            continue

        # Required keyword check
        if not any(ok in message_text for ok in ok_words):
            print("❌ No required keyword, skipping.")
            append_to_csv(csv_path, [user_name, "skipped_no_match", message_text])
            driver.back()
            time.sleep(1)
            continue

        # Send message
        reply_box = driver.find_element(By.NAME, "send_message")
        reply = random.choice(message_templates)
        reply_box.send_keys(reply)

        send_button = driver.find_element(By.ID, "send_button")
        send_button.click()

        print("✅ Message sent!")
        append_to_csv(csv_path, [user_name, "sent", reply])

        time.sleep(delay_sec)
        driver.back()

    except Exception as e:
        print("⚠️ Error while processing:", e)
        driver.back()
        continue

print("🎉 All done!")
driver.quit()