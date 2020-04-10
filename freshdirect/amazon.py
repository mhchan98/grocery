import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
from freshdirect.get_slot import run_loop
import time

def find_slots(driver):
    result = []
    alerts = driver.find_elements_by_class_name('ufss-slotselect-unavailable-alert')
    for alert in alerts:
        if 'No delivery windows available. New windows are released throughout the day.' == alert.text:
            result.clear()
            break
        else:
            result.append(alert.text)
    return result


def refresh(driver):
    driver.refresh()
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.XPATH, '//*[@id="shipoption-select"]/div/div/div/div/div[1]/div[4]/div[1]/h3')))
    time.sleep(1)


def loop_until_find_slot(driver, retries=None, refresh_quiet_time=0):
    slots=[]
    while retries is None or retries > 0:
        slots = find_slots(driver)
        if len(slots) > 0:
            print(f"{datetime.datetime.now()}: Found Slots: " + slots)
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
