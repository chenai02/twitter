import json
import time
from selenium import webdriver

# 可参考来打开chromedriver
# driverOptions = webdriver.ChromeOptions()
#     # r代表后面的字符串斜杠不转义，''表示python识别空格
#     driverOptions.add_argument(r"user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome for Testing\User Data")
#     driverOptions.binary_location = r"D:\Program Files\utils\chrome-win64\chrome.exe"
#     # 指定 ChromeDriver 的路径
#     driver_path = r"D:\Program Files\utils\chromedriver-win64\chromedriver.exe"
#     # 创建 ChromeDriver 服务
#     s = Service(executable_path=driver_path)
#     driver = webdriver.Chrome(service=s, options=driverOptions)
# 生成cookies
browser = webdriver.Chrome()

try:
    browser.get("https://twitter.com/i/flow/login") # https://twitter.com/i/flow/login        # https://www.pixiv.net/
    time.sleep(45)  # 30s内登录等待退出

finally:
    dictCookies = browser.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    print(jsonCookies)
    with open('123.json', 'w') as f:
        f.write(jsonCookies)
    browser.quit()
