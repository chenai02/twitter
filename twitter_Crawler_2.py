import json
import time
from FixedSizeQueue import FixedSizeQueue
from download_pic import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchWindowException
import requests
from PIL import Image
from io import BytesIO
from datetime import datetime

def download_image(url, save_path):
    try:
        # 发送HTTP请求
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功

        # 读取图片数据
        image_data = response.content

        # 打开图片
        image = Image.open(BytesIO(image_data))

        # 保存图片
        image.save(save_path)
        print(f"Image successfully downloaded and saved to {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image from {url}: {e}")
    except IOError as e:
        print(f"Error saving the image: {e}")


def download_images(urls, save_directory):
    # 确保保存目录存在
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    count = 0
    save_path = os.path.join(save_directory, f"image_{count}.jpg")

    for i, url in enumerate(urls):
        while os.path.exists(save_path):
            save_path = os.path.join(save_directory, f"image_{count + 1}.jpg")
            count += 1
        download_image(url, save_path)


def crash_new(twitter_user, content_queue, count):
    tweet_text, date, image_urls, uuid = '', '-1', [], ''
    try:
        tweets = driver.find_elements(By.CSS_SELECTOR, "article")

        if len(tweets) == 0:
            return '', -1, []
        elif len(tweets) >= 10:
            tweets = tweets[:10]
        # 解析目标推文
        for tweet in tweets:
            soup = BeautifulSoup(tweet.get_attribute("innerHTML"), "html.parser")


            # 获取日期
            date = datetime.fromisoformat(soup.find("time")["datetime"].replace("Z", "+00:00")).strftime('%Y%m%d%H%M%S')

            # 生成唯一ID
            uuid = twitter_user + '_' + date

            if content_queue.contains(uuid):
                date = '-1'
                time.sleep(10)
                return tweet_text, date, image_urls, uuid
            # 获取推文内容
            tweet_text = soup.find("div", {"data-testid": "tweetText"}).get_text()

            # 获取互动数据
            engagements = soup.find_all(
                "span", {"data-testid": "app-text-transition-container"}
            )
            comments = engagements[0].get_text() if len(engagements) > 0 else "0"
            retweets = engagements[1].get_text() if len(engagements) > 1 else "0"
            likes = engagements[2].get_text() if len(engagements) > 2 else "0"
            views = engagements[3].get_text() if len(engagements) > 3 else "0"

            # 获取图片URL
            image_elements = soup.find_all("img", {"alt": "Image"})
            for image_element in image_elements:
                src = image_element.attrs.get("src", None)
                if src:
                    image_urls.append(src)

            # 打印结果
            print(f"日期: {date}")
            print(f"推文内容: {tweet_text}")
            print(f"评论数: {comments}")
            print(f"转推数: {retweets}")
            print(f"点赞数: {likes}")
            print(f"观看数: {views}")
            if image_urls:
                print("图片URL:")
                for url in image_urls:
                    print(url)

            print("-" * 40)

            save_dir = os.path.join('image/', uuid)
            if image_urls:
                download_images(image_urls, save_dir)
            content_queue.enqueue(uuid)
            time.sleep(10)
            if count == 0:
                return tweet_text, date, image_urls, uuid
    except NoSuchWindowException:
        print("No such window: target window already closed.")
        return '', '-2', [], uuid
    except WebDriverException:
        print("WebDriverException occurred.")
        return '', '-2', [], uuid
    finally:
        return tweet_text, date, image_urls, uuid


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
    # 第一次爬取时，只需要爬一条消息
    count = 0
    while True:
        try:
            with open("./twitterUrl.txt", "r", encoding="utf-8") as file:
                for line in file:
                    try:
                        # 去除首尾空白字符
                        line = line.strip()
                        if not line:
                            continue
                        driver.get(line)
                        print("准备爬取推文中.....")
                        time.sleep(15)
                        name = driver.find_elements(
                            By.XPATH,
                            '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]',
                        )
                        if not name[0].text:
                            continue

                        twitter_user = name[0].text
                        tweet_text, date, image_urls, uuid = crash_new(twitter_user, content_queue, count)
                        if date == '-1':
                            continue
                        elif date == '-2':
                            break
                    except TimeoutException:
                        print("Loading the page timed out.")
                        time.sleep(10)
                    except NoSuchWindowException:
                        print("The target window is already closed.")
                        break
                    except WebDriverException as e:
                        print(f"WebDriverException occurred: {e}")
                        time.sleep(10)
                        continue
                    except Exception as e:
                        print(f"other error: {e}")
                        time.sleep(10)
        except BaseException as error:
            print("open file has a error, ", str(error))
        count = 1
        time.sleep(8000)
