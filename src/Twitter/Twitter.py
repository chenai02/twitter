import os
import requests
import pytz
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchWindowException
from src.FixedSizeQueue.FixedSizeQueue import FixedSizeQueue
from src.MyMQ.myMQ import MQ_init_From_Config
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from datetime import datetime
from PIL import Image
from io import BytesIO

class Twitter:
    def __init__(self, cache_size, config, driver):
        self.content_queue = FixedSizeQueue(cache_size)
        # self.my_mq = MQ_init_From_Config(config)
        self.driver = driver
        self.count = 0

    def find_elements(self, line, xpath, path):
        try:
            # 去除首尾空白字符
            url = line.strip()
            if not line:
                return -1, -1
            self.driver.get(url)
            print("准备爬取推文，请等待15秒")
            time.sleep(15)
            name = self.driver.find_elements(xpath, path)
            if not name[0].text:
                return -1, -1
            twitter_user = name[0].text
            return url, twitter_user
        except BaseException as error:
            print("open file has a error, ", str(error))
            raise

    def parse_message(self, soup, currentTime):
        # 获取日期
        print(soup.find("time")["datetime"])
        dt = datetime.strptime(soup.find("time")["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
        # 设置为UTC时区
        dt = dt.replace(tzinfo=pytz.UTC)
        # 转换为中国时区
        dt = dt.astimezone(pytz.timezone("Asia/Shanghai"))
        if currentTime > dt:
            return -1, -1, -1
        date = dt.strftime("%Y-%m-%d %H:%M:%S")
        # 获取推文内容
        tweet_text = soup.find("div", {"data-testid": "tweetText"}).get_text()

        # 获取互动数据
        # engagements = soup.find_all(
        #     "span", {"data-testid": "app-text-transition-container"}
        # )
        # comments = engagements[0].get_text() if len(engagements) > 0 else "0"
        # retweets = engagements[1].get_text() if len(engagements) > 1 else "0"
        # likes = engagements[2].get_text() if len(engagements) > 2 else "0"
        # views = engagements[3].get_text() if len(engagements) > 3 else "0"
        # 打印结果
        # print(f"日期: {date}")
        # print(f"评论数: {comments}")
        # print(f"转推数: {retweets}")
        # print(f"点赞数: {likes}")
        # print(f"观看数: {views}")
        # 获取图片URL
        image_elements = soup.find_all("img", {"alt": "Image"})
        return date, image_elements, tweet_text

    def crash_new(self, twitter_user, currentTime):
        tweet_text, date, image_urls, uuid = '', -1, [], ''
        try:
            tweets = self.driver.find_elements(By.CSS_SELECTOR, "article")
            if len(tweets) == 0:
                return '', -1, []
            elif len(tweets) >= 10:
                tweets = tweets[:10]
            # 解析目标推文
            for tweet in tweets:
                soup = BeautifulSoup(tweet.get_attribute("innerHTML"), "html.parser")
                date, image_elements, tweet_text = self.parse_message(soup, currentTime)

                if date == -1:
                    return '', -1, []
                uuid = (str(twitter_user) + '_' + date).replace(" ", "")
                if self.content_queue.contains(uuid):
                    date = '-1'
                    return tweet_text, date, image_urls, uuid
                for image_element in image_elements:
                    src = image_element.attrs.get("src", None)
                    if src:
                        image_urls.append(src)
                if image_urls:
                    print("图片URL:")
                    for url in image_urls:
                        print(url)

                print("-" * 40)

                save_dir = os.path.join('image/', uuid)
                if image_urls:
                    Twitter.download_images(image_urls, save_dir)
                if self.count == 0:
                    return tweet_text, date, image_urls, uuid
        except NoSuchWindowException:
            print("No such window: target window already closed.")
            return '', '-2', [], uuid
        except WebDriverException:
            print("WebDriverException occurred.")
            return '', '-2', [], uuid
        finally:
            return tweet_text, date, image_urls, uuid

    @staticmethod
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

    @staticmethod
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
            Twitter.download_image(url, save_path)
