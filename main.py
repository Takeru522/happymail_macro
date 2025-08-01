mport json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from undetected_chromedriver.v2 import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

# Load login credentials from config
with open("config/credentials.json", "r", encoding="utf-8") as f:
    credentials = json.load(f)
LOGIN_ID = credentials["login_id"]
PASSWORD = credentials["password"]

# Mobile emulation
mobile_emulation = { "deviceName": "iPhone SE" }

# Chrome options
options = ChromeOptions()
options.add_experimental_option("mobileEmulation", mobile_emulation)
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

# Launch browser
driver = Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

# Go to HappyMail
driver.get("https://happymail.co.jp")

# === STEP 1: Click Login Button on Home Screen ===
try:
    login_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "ログイン")))
    login_button.click()
except Exception as e:
    print("❌ Failed to click login:", e)

# === STEP 2: Enter ID and Password ===
try:
    id_input = wait.until(EC.presence_of_element_located((By.NAME, "login_id")))
    pw_input = wait.until(EC.presence_of_element_located((By.NAME, "login_pw")))

    id_input.send_keys(LOGIN_ID)
    pw_input.send_keys(PASSWORD)

    login_submit = driver.find_element(By.ID, "login_form_submit")
    login_submit.click()

    print("✅ Logged in successfully (attempted)")
except Exception as e:
    print("❌ Login failed:", e)

# === STEP 3: Pause to View Result ===
time.sleep(10)
driver.quit()