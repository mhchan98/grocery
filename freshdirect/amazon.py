import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
from freshdirect.get_slot import run_loop
import time


def find_slots(driver):
    if has_alert(driver) and section_match_no_delivery(driver):
        return []
    else:
        return ['find some slot']


def has_alert(driver):
    try:
        alerts = driver.find_elements_by_class_name('ufss-slotselect-unavailable-alert')
        result = False
        for alert in alerts:
            if 'No delivery windows available. New windows are released throughout the day.' == alert.text:
                result = True
                break
        return result
    except Exception as e:
        print(f"{datetime.datetime.now()}: Exception occurred while has_alert: {e}")
        return False


def section_match_no_delivery(driver):
    try:
        element = driver.find_element_by_css_selector(
            '#shipoption-select > div > div > div > div > div.ufss-widget-grid > div:nth-child(4) ')
        return element.text == 'Select a time\nBe sure to chill your perishables immediately upon receiving your order.\nNo delivery windows available. New windows are released throughout the day.'
    except Exception as e:
        print(f"{datetime.datetime.now()}: Exception occurred while section_match_no_delivery: {e}")
        return False


def refresh(driver):
    driver.refresh()
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.XPATH, '//*[@id="shipoption-select"]/div/div/div/div/div[1]/div[4]/div[1]/h3')))
    time.sleep(1)


def select_slot(driver):
    today_id = datetime.datetime.now().strftime('%Y%m%d')
    element = driver.find_element_by_xpath(f'//*[@id="{today_id}"]/div[1]/div/ul/li/span/span/div/div[2]/span/span/button/div')
    print(f"{datetime.datetime.now()}: click {today_id} free slot")
    element.click()
    continue_btn = driver.find_element_by_xpath('//*[@id="shipoption-select"]/div/div/div/div/div[2]/div[3]/div/span/span/span/input')
    time.sleep(0.2)
    print(f"{datetime.datetime.now()}: click continue")
    continue_btn.click()
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.XPATH, '//*[@id="checkoutDisplayPage"]/div[1]/div[2]/div[2]/div[2]/h1')))
    time.sleep(0.2)
    print(f"{datetime.datetime.now()}: click continue2")
    continue2_btn = driver.find_element_by_xpath('//*[@id="continue-top"]')
    continue2_btn.click()


def loop_until_find_slot(driver, retries=None, refresh_quiet_time=0):
    slots=[]
    while retries is None or retries > 0:
        slots = find_slots(driver)
        if len(slots) > 0:
            print(f"{datetime.datetime.now()}: Found Slots: {slots}")
            select_slot(driver)
            return slots
        else:
            print(f"{datetime.datetime.now()}: Found no slot")
            refresh(driver)
        if retries is not None:
            retries -= 1
    return slots


def main():
    run_loop('https://www.amazon.com/', loop_until_find_slot)


if __name__ == '__main__':
    main()
