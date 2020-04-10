from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
import datetime

from freshdirect.get_slot import run_loop


def get_proxies():
    driver = webdriver.Chrome('../chromedriver.exe')
    driver.get("https://sslproxies.org/")
    driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 20).until(visibility_of_element_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//th[contains(., 'IP Address')]"))))
    ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 1]")))]
    ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 2]")))]
    driver.quit()
    proxies = []
    for i in range(0, len(ips)):
        proxies.append(ips[i]+':'+ports[i])
    print(proxies)
    return proxies


def click_select_time(driver):
    select_time_btn = driver.find_element_by_class_name('orange')
    select_time_btn.click()


def find_slots(driver):
    result = []
    for col_idx in range(1, 6+1):
        for row_idx in range(5):
            slot = driver.find_element_by_id(f"ts_d{col_idx}_ts{row_idx}_time")
            if "tsSoldoutC" not in slot.get_attribute("class").split(' '):
                print(f"Find slot day_{col_idx}, slot_{row_idx}: {slot.text}")
                result.append(slot.text)
            else:
                pass
                #print(f"No slot day_{col_idx}, slot_{row_idx}: {slot.text}")
    return result


def back_to_select(driver):
    btn = driver.find_element_by_xpath('//*[@id="timeslot-tab"]/div/span[2]/button')
    btn.click()


def back_to_select_and_wait(driver):
    back_to_select(driver)
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.XPATH, '//*[@id="ec-drawer"]/div/div/ul/li[2]/div/div/button')))


def click_select_time_and_wait(driver):
    click_select_time(driver)
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.XPATH, '//*[@id="timeslot-tab"]/div/span[2]/button')))


def loop_until_find_slot(driver, retries=None, refresh_quiet_time=0):
    click_select_time_and_wait(driver)
    slots=[]
    while retries is None or retries > 0:
        slots = find_slots(driver)
        if len(slots) > 0:
            print(f"{datetime.datetime.now()}: Found Slots: " + slots)
            return slots
        else:
            print(f"{datetime.datetime.now()}: Found no slot")
            back_to_select_and_wait(driver)
            click_select_time_and_wait(driver)
        if retries is not None:
            retries -= 1
    back_to_select_and_wait(driver)
    return slots


def main():
    run_loop('https://www.freshdirect.com/', loop_until_find_slot)


if __name__ == '__main__':
    main()
