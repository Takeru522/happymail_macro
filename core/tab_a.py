# core/tab_a.py

import time
import random
import os
from selenium.webdriver.common.by import By
from utils import load_json, append_to_csv

def run_tab_a(driver):
    # === Settings ===
    settings = load_json("config/tab_a_settings.json")
    ng_words = settings["ng_words"]
    ok_words = settings["required_keywords"]
    templates = settings["messages"]["first"]
    delay = settings["delay_between_messages_sec"]

    # === Memory ===
    messaged_users = set()
    csv_path = "output/messages_sent.csv"
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for line in f.readlines()[1:]:
                messaged_users.add(line.split(",")[0].strip())

    # === Go to 未返信 ===
    driver.get("https://happymail.co.jp/sp/app/html/msglist.php?ad=0&jmode=3")
    time.sleep(2)

    threads = driver.find_elements(By.CSS_SELECTOR, "li.ds_user_post_link_item_r a")
    print(f"📬 Found {len(threads)} threads")

    for index, thread in enumerate(threads):
        href = thread.get_attribute("href")
        if "uid=" in href:
            user_id = href.split("uid=")[-1].split("&")[0]
        else:
            user_id = f"User{index}"

        if user_id in messaged_users:
            print(f"⏭ {user_id} already messaged")
            continue

        try:
            thread.click()
            time.sleep(2)

            msg = driver.find_element(By.CLASS_NAME, "fs13px").text

            if any(ng in msg for ng in ng_words):
                print("🚫 NG word match")
                append_to_csv(csv_path, [user_id, "skipped_ng", msg])
                driver.back()
                time.sleep(1)
                continue

            if not any(ok in msg for ok in ok_words):
                print("❌ No required keyword")
                append_to_csv(csv_path, [user_id, "skipped_no_match", msg])
                driver.back()
                time.sleep(1)
                continue

            reply = random.choice(templates)
            driver.find_element(By.NAME, "send_message").send_keys(reply)
            driver.find_element(By.ID, "send_button").click()
            print("✅ Sent to", user_id)
            append_to_csv(csv_path, [user_id, "sent", reply])

            time.sleep(delay)
            driver.back()

        except Exception as e:
            print("⚠️ Error with", user_id, ":", e)
            driver.back()
            continue