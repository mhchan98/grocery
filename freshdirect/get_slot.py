import time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import *
import datetime
import winsound
import threading


def create_driver(url):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options,
                              executable_path='../chromedriver.exe')  # Optional argument, if not specified will search path.
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    driver.get(url)
    return driver


def alert_user(slots):
    freq = 2500
    dur = 5000
    class AlertThread(threading.Thread):
        def run(self):
            self.stopped = False
            while not self.stopped:
                winsound.Beep(freq, dur)
                time.sleep(1)
                print(f"Stopped: {self.stopped}")

    thread = AlertThread()
    thread.start()
    input(f"Found slot({slots}) - please order: Press any key to stop the beep")
    thread.stopped = True
    print("Waiting for alert thread to die")
    thread.join()
    print("alert thread is dead")


def main(url: str, loop_func):
    driver = create_driver(url)
    input("""
     Please log in to FreshDirect and navigate to the checkout screen and then press enter to continue
    """)
    slots =[]
    while True:
        try:
            if len(slots) > 0:
                alert_user(slots)

            cmd = input("""Please enter how many times you want to loop for result:
                enter * for infinite loop
                enter q to quit
                 """)
            if cmd == "*":
                slots = loop_func(driver, retries=None)
            if cmd == "q":
                driver.quit()
                break
            else:
                slots = loop_func(driver, retries=int(cmd))
        except Exception as e:
            print(f"Exception occurred: {e}")