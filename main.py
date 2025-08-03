
from core.login import login_with_cookies, save_cookies
from core.tab_a import run_tab_a
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def create_driver():
    options = Options()
    options.add_experimental_option("mobileEmulation", {"deviceName": "iPhone SE"})
    return webdriver.Chrome(options=options)

def main():
    driver = create_driver()

    # 👇 FIRST TIME ONLY:
    # Uncomment this and run the script.
    # save_cookies(driver)

    # 👇 After that, comment the above and use this:
    login_with_cookies(driver)
    run_tab_a(driver)
    input("✅ Browser is running. Press Enter to quit.")
    driver.quit()

if __name__ == "__main__":
    main()
