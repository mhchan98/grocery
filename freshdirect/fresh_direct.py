from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver import ActionChains
import datetime
import time
import random
import traceback


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
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.ID, 'subtotalbox2')))
    select_time_btn = driver.find_element_by_class_name('orange')
    move_mouse(driver, select_time_btn)
    print(f"{datetime.datetime.now()}: Clicking select time")
    select_time_btn.click()


def move_mouse(driver, element):
    action_chains = ActionChains(driver)
    action_chains.move_to_element(element).perform()


def move_mouse_to_headers(driver):
    num_headers_try = random.randint(1, 4)
    print(f"{datetime.datetime.now()}: move_mouse_to_headers ({num_headers_try})")
    while num_headers_try > 0:
        col_num = random.randint(0, 6)
        try:
            move_mouse(driver, driver.find_element_by_xpath(f'//*[@id="ts_d{col_num}_hC"]'))
            random_sleep(0.75)
            num_headers_try -= 1
        except Exception as e:
            if "javascript error: Failed to execute 'elementsFromPoint'" not in f"{e}":
                print(f"Exception occurred while moving to column header {col_num}, num_headers_try({num_headers_try}): {e}")
                #traceback.print_exc()


def find_slots(driver):
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.ID, 'ts_d1_ts0_time')))
    result = []
    for col_idx in range(1, 6+1):
        for row_idx in range(5):
            try:
                slot = driver.find_element_by_id(f"ts_d{col_idx}_ts{row_idx}_time")
                if "tsSoldoutC" not in slot.get_attribute("class").split(' '):
                    print(f"Find slot day_{col_idx}, slot_{row_idx}: {slot.text}")
                    result.append(slot.text)
                else:
                    pass
                    #print(f"No slot day_{col_idx}, slot_{row_idx}: {slot.text}")
            except Exception as e:
                print(f"Exception processing slot day_{col_idx}, slot_{row_idx}: {e}")
                traceback.print_exc()

    if len(result) > 0:
        return result

    move_mouse_to_headers(driver)
    header = driver.find_element_by_css_selector('#timeslot-tab > div > span.cancel.hidden.right > button')
    move_mouse(driver, header)
    in_slot = True
    if random.random() > 0.5:
        print(f"{datetime.datetime.now()}: click cancel")
        header.click()
        in_slot = False

    if random.random() > 0.5:
        in_slot = ping_pong(driver, in_slot, click=random.randint(1, 5))

    if random.random() > 0.8:
        # 20% chance to have a long wait
        print(f"{datetime.datetime.now()}: random long wait hit")
        in_slot = ping_pong(driver, in_slot, click=random.randint(12, 15))

    return result


def click_cancel(driver):
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.ID, 'ts_d1_ts0_time')))
    btn = driver.find_element_by_css_selector('#timeslot-tab > div > span.cancel.hidden.right > button')
    move_mouse(driver, btn)
    btn.click()


def ping_pong(driver, in_slot, click=10):
    print(f"{datetime.datetime.now()}: ping pong ({click})")
    while click > 0:
        if in_slot:
            click_cancel(driver)
            in_slot = False
        else:
            click_select_time(driver)
            in_slot = True
        random_sleep(0.8)
        click -= 1

    return in_slot


def back_to_select_and_wait(driver):
    print(f"{datetime.datetime.now()}: refreshing")
    driver.refresh()
    random_sleep(random.randint(1, 4))


def click_select_time_and_wait(driver):
    click_select_time(driver)
    random_sleep(random.randint(1, 10))


def site_blocked(driver):
    body_element = driver.find_element_by_css_selector('body')
    if "Access Denied\nYou don\'t have permission to access" in body_element.text:
        return True
    else:
        return False


def random_sleep(sec, max_adj_rate = 0.3):
    adjustment = (random.random() - 0.5)/0.5 * (sec * max_adj_rate)
    sleep_time = sec + adjustment
    time.sleep(sleep_time)


def resume(driver, random_level=0):
    driver.get('https://www.freshdirect.com/')
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.ID, 'locabar_popupcart_trigger')))
    element = driver.find_element_by_id('locabar_popupcart_trigger')
    move_mouse(driver, element)
    print(f"{datetime.datetime.now()}: Clicking the menu bar")
    element.click()

    random_move_menu(driver)

    for i in range(random_level * 3):
        if random.random() > 0.5:
            random_move_menu(driver)
        if random.random() > 0.5:
            random_move_donate(driver)

    random_move_donate(driver)

    # checkout
    element = driver.find_element_by_xpath('//*[@id="cartheader"]/div/div[3]/form/button')
    random_sleep(5)
    move_mouse(driver, element)
    print(f"{datetime.datetime.now()}: Clicking the checkout button")
    element.click()
    random_sleep(1)


def random_move_donate(driver):
    # move to donate
    donate_selectors = [
        '#cartCarousels > div > div > div > div > ul > li',
        '#cartCarousels > div > div > div > div > ul > li + li',
        '#cartCarousels > div > div > div > div > ul > li + li + li',
    ]
    move_times = random.randint(1, 2)
    last_idx = None
    while move_times > 0:
        idx = random.randint(0, len(donate_selectors) - 1)
        while last_idx is not None and idx == last_idx:
            idx = random.randint(0, len(donate_selectors) - 1)
        last_idx = idx

        selector = donate_selectors[idx]
        try:
            item = driver.find_element_by_css_selector(selector)
            print(f"{datetime.datetime.now()}: moving to {idx} move_times: ({move_times})")
            move_mouse(driver, item)
            random_sleep(0.75)
            move_times -= 1
        except Exception as e:
            print(f"{datetime.datetime.now()}: Exception occurred in resume moving menu {idx} - remaining retries({move_times}): {e}")
            traceback.print_exc()


def random_move_menu(driver):
    # move menu
    menus_xpaths = [
        ('/html/body/div[8]/nav/div/div[1]/ul/li[1]', 'prepared'),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[2]', "fruit"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[3]', "vegetables"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[4]', "meat"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[5]', "seafood"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[6]', "dairy"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[7]', "deli"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[8]', "pastry"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[9]', "grocery"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[10]', "frozen"),
        ('/html/body/div[8]/nav/div/div[1]/ul/li[11]', "beer"),
    ]
    WebDriverWait(driver, 5).until(
        visibility_of_all_elements_located((By.XPATH, '//*[@id="cartheader"]/div/div[3]/form/button')))
    random_sleep(1)
    move_times = random.randint(1, 3)
    while move_times > 0:
        idx = random.randint(0, len(menus_xpaths) - 1)
        xpath, desc = menus_xpaths[idx]
        try:
            menu_item = driver.find_element_by_xpath(xpath)
            print(f"{datetime.datetime.now()}: moving to {desc} move_times: ({move_times})")
            move_mouse(driver, menu_item)
            random_sleep(0.75)
            move_times -= 1
        except Exception as e:
            print(f"{datetime.datetime.now()}: Exception occurred in resume moving menu {idx} - remaining retries({move_times}): {e}")
            traceback.print_exc()


def resume_with_retry(driver, resume_retries=5):
    idx = 0
    while resume_retries > 0:
        try:
            print(f"{datetime.datetime.now()}: Trying to resume")
            resume(driver, random_level=idx)
            click_select_time_and_wait(driver)
            return
        except Exception as e:
            print(f"{datetime.datetime.now()}: Exception occurred in resume_with_retry - remaining retries({resume_retries}): {e}")
            traceback.print_exc()
            random_sleep(2 * (idx + 1))
            resume_retries -= 1
            idx += 1


def loop_until_find_slot(driver, retries=None, refresh_quiet_time=0):
    click_select_time_and_wait(driver)
    slots=[]
    while retries is None or retries > 0:
        try:
            slots = find_slots(driver)
            if len(slots) > 0:
                print(f"{datetime.datetime.now()}: Found Slots: " + slots)
                return slots
            else:
                print(f"{datetime.datetime.now()}: Found no slot")
                random_sleep(1)
                back_to_select_and_wait(driver)
                click_select_time_and_wait(driver)
        except Exception as e:
            print(f"{datetime.datetime.now()}: Exception occurred in loop_until_find_slot: {e}")
            traceback.print_exc()
            random_sleep(5)
            if site_blocked(driver):
                resume_with_retry(driver)
            else:
                raise e

        if retries is not None:
            retries -= 1
    back_to_select_and_wait(driver)
    return slots


def main():
    run_loop('https://www.freshdirect.com/', loop_until_find_slot)


if __name__ == '__main__':
    main()
