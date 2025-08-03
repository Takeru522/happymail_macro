import time
import os
import random
from selenium.webdriver.common.by import By
from utils import load_json, append_to_csv

def run_tab_a(driver):
    print("📬 Loading settings for Tab A...")
    settings = load_json("config/tab_a_settings.json")
    ng_words = settings["ng_words"]
    ok_words = settings["required_keywords"]
    message_templates = settings["messages"]["first"]
    delay_sec = settings["delay_between_messages_sec"]

    # ✅ Load already-messaged users from CSV
    csv_path = "output/messages_sent.csv"
    messaged_users = set()
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                user = line.split(",")[0].strip()
                messaged_users.add(user)

    # ✅ Find all message thread links
    print("📥 Scanning 未返信 threads...")
    time.sleep(3)
    threads = driver.find_elements(By.CSS_SELECTOR, "li.ds_user_post_link_item_r a")
    print(f"📬 Found {len(threads)} threads")

    for index, thread in enumerate(threads):
        try:
            # ✅ Extract UID from href
            href = thread.get_attribute("href")
            if "uid=" in href:
                user_name = href.split("uid=")[-1].split("&")[0]
            else:
                user_name = f"User{index}"

            if user_name in messaged_users:
                print(f"⏭ Already messaged {user_name}, skipping")
                continue

            print(f"➡ Opening thread for {user_name}")
            thread.click()
            time.sleep(2)

            # 🔍 Save HTML for debugging
            with open(f"debug_thread_{user_name}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            # ✅ Try multiple selectors to get message
            message_element = None
            for selector in ["p.fs13px", "p.balloon_other", "div.fs13px", "span.fs13px","message_body"]:
                try:
                    message_element = driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue

            if not message_element:
                print(f"⚠️ Could not find message element for {user_name}")
                append_to_csv(csv_path, [user_name, "skipped_no_message", ""])
                driver.back()
                time.sleep(1)
                continue

            message_text = message_element.text
            print("📝 Message:", message_text)

            # ❌ NG word filter
            if any(ng in message_text for ng in ng_words):
                print("🚫 Skipped (NG word detected)")
                append_to_csv(csv_path, [user_name, "skipped_ng", message_text])
                driver.back()
                time.sleep(1)
                continue

            # ✅ Required keyword filter
            if not any(ok in message_text for ok in ok_words):
                print("❌ Skipped (no required keyword)")
                append_to_csv(csv_path, [user_name, "skipped_no_match", message_text])
                driver.back()
                time.sleep(1)
                continue

            # ✉️ Send reply
            reply = random.choice(message_templates)
            reply_box = driver.find_element(By.NAME, "send_message")
            reply_box.send_keys(reply)
            send_button = driver.find_element(By.ID, "send_button")
            send_button.click()

            print("✅ Message sent!")
            append_to_csv(csv_path, [user_name, "sent", reply])
            time.sleep(delay_sec)
            driver.back()

        except Exception as e:
            print(f"⚠️ Error with {user_name} :", e)
            driver.back()
            continue