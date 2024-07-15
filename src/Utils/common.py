import threading
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from loguru import logger

def process_data(data, thread_id):
    # 这里可以添加处理数据的逻辑
    logger.info(f"Thread {thread_id}: Processing data... Length of data is {data}\n")


def create_thread(data, num_threads_count):
    def worker(data, thread_id):
        process_data(data, thread_id)

    return threading.Thread(target=worker, args=(data, num_threads_count))


def set_cookie(self):
    # 可参考来打开chromedriver
    driverOptions = webdriver.ChromeOptions()
    # r代表后面的字符串斜杠不转义，''表示python识别空格
    driverOptions.add_argument(r"user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome for Testing\User Data")
    driverOptions.binary_location = r"D:\Program Files\utils\chrome-win64\chrome.exe"
    # 指定 ChromeDriver 的路径
    driver_path = r"D:\Program Files\utils\chromedriver-win64\chromedriver.exe"
    # 创建 ChromeDriver 服务
    s = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=s, options=driverOptions)
    # 生成cookies
    browser = webdriver.Chrome()

    try:
        browser.get(
            "https://twitter.com/i/flow/login")  # https://twitter.com/i/flow/login        # https://www.pixiv.net/
        time.sleep(45)  # 30s内登录等待退出

    finally:
        dictCookies = browser.get_cookies()
        jsonCookies = json.dumps(dictCookies)
        logger.info(jsonCookies)
        with open('../../123.json', 'w') as f:
            f.write(jsonCookies)
        browser.quit()


if __name__ == "__main__":
    file_path = "./twitterUrl.txt"
    threads = []
    num_threads_count = 0

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            thread = create_thread(line, num_threads_count)
            threads.append(thread)
            num_threads_count += 1
            thread.start()

    for thread in threads:
        thread.join()
