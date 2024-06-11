import json
import time
from FixedSizeQueue import FixedSizeQueue
from download_pic import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup


def download_new(name):
    while len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='tweetText']")):
        try:
            for data in driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid='tweetText']"
            )[0:7]:
                # print(len(driver.find_elements(By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']")))
                # print(len(data.find_elements(By.TAG_NAME, "img")))    # 调试时使用
                for img in data.find_elements(By.TAG_NAME, "img"):
                    src = img.get_attribute("src")
                    if "profile_images" not in src and "media" in src:
                        string_list.append(
                            src[: src.find("?")] + "?format=png&name=large"
                        )  # &name=large
                driver.execute_script(
                    """
                    var dataElements = document.querySelectorAll("div[data-testid='cellInnerDiv']");
                    if(dataElements.length > 0) {
                        dataElements[0].remove();
                    }
                    """
                )
                time.sleep(0.5)
                if (
                    len(
                        driver.find_elements(
                            By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']"
                        )
                    )
                    == 0
                ):
                    time.sleep(2)
                print("next", end=" ")
        except BaseException as error:
            print("what?")
            print(str(error))
            continue
    print("")
    get_url_pic(string_list, len(string_list), name)
    print(f"共下载{len(string_list)}张图片")


def crash_new(name):
    while True:
        try:
            tweets = driver.find_elements(By.CSS_SELECTOR, "article")
            if len(tweets) == 0:
                continue
            # 解析目标推文
            for tweet in tweets:
                soup = BeautifulSoup(tweet.get_attribute("innerHTML"), "html.parser")

                # 获取用户名
                username = soup.find("div", {"dir": "ltr"}).get_text()

                # 获取日期
                date = soup.find("time")["datetime"]

                # 获取推文内容
                tweet_text = soup.find("div", {"data-testid": "tweetText"}).get_text()

                # 获取视频时长（假设有视频）
                video_duration = (
                    soup.find("span", {"data-testid": "videoDuration"}).get_text()
                    if soup.find("span", {"data-testid": "videoDuration"})
                    else None
                )

                # 获取互动数据
                engagements = soup.find_all(
                    "span", {"data-testid": "app-text-transition-container"}
                )
                comments = engagements[0].get_text() if len(engagements) > 0 else "0"
                retweets = engagements[1].get_text() if len(engagements) > 1 else "0"
                likes = engagements[2].get_text() if len(engagements) > 2 else "0"
                views = engagements[3].get_text() if len(engagements) > 3 else "0"

                # 获取图片URL
                image_urls = []
                image_elements = soup.find_all("img", {"alt": "Image"})
                for image_element in image_elements:
                    src = image_element.attrs.get("src", None)
                    if src:
                        image_urls.append(src)

                # 打印结果
                print(f"用户名: {username}")
                print(f"日期: {date}")
                print(f"推文内容: {tweet_text}")
                if video_duration:
                    print(f"视频时长: {video_duration}")
                print(f"评论数: {comments}")
                print(f"转推数: {retweets}")
                print(f"点赞数: {likes}")
                print(f"观看数: {views}")
                if image_urls:
                    print("图片URL:")
                    for url in image_urls:
                        print(url)

                print("-" * 40)
                return tweet_text, date
            break
        except BaseException as error:
            print(str(error))
            continue
    print("name:", name)


def crash_new2(name):
    while True:
        try:
            data = driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid='cellInnerDiv']"
            )
            if len(data) == 0 or not data[0].text or data[0].text.strip() == "":
                continue
            print("test", data[0].text)
            break
        except BaseException as error:
            print("what?")
            print(str(error))
            continue
    print("name:", name)


if __name__ == "__main__":
    # 初始化
    chrome_options = ChromeOptions()
    chrome_options.add_argument("window-position=660,0")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(5)
    string_list = []

    try:
        driver.get("https://twitter.com/i/flow/login")
    except TimeoutException:
        driver.execute_script("window.stop()")
    driver.set_page_load_timeout(60)

    # 设置cookie
    print("设置cookie中.....")
    cookies = json.load(open("123.json", "r"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    # 创建队列
    content_queue = FixedSizeQueue(100)
    print("访问推特页面中.....")
    try:
        with open("./twitterUrl.txt", "r", encoding="utf-8") as file:
            for line in file:
                driver.get(line)
                print("准备爬取推文中.....")
                time.sleep(3)
                name = driver.find_elements(
                    By.XPATH,
                    '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]',
                )
                page_source = driver.page_source
                twitter_user = name[0].text
                # 创建twitter名称文件夹
                if not os.path.exists(twitter_user):
                    os.makedirs(twitter_user)
                tweet_text, date = crash_new(twitter_user)
                if not content_queue.contains(tweet_text):
                    content_queue.enqueue(tweet_text)
                else:
                    ()
                
    except BaseException as error:
        print(str(error))