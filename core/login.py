
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from utils import load_json

def create_driver():
    mobile_emulation = { "deviceName": "iPhone SE" }
    options = Options()
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=ja-JP")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def login(driver):
    credentials = load_json("config/credentials.json")
    email = credentials["email"]
    password = credentials["password"]

    driver.get("https://happymail.co.jp/sp/app/html/login.php")
    time.sleep(2)

    driver.find_element(By.NAME, "mailad").send_keys(email)
    driver.find_element(By.NAME, "pswd").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)