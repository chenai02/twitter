import json
import time
import logging
import requests
import aiohttp
import asyncio
from FixedSizeQueue import FixedSizeQueue
from download_pic import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchWindowException


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

async def download_image(session, url, save_directory, file_name=None):
    """
    异步下载图片并保存到指定目录。
    
    :param session: aiohttp 客户端会话
    :param url: 图片的 URL
    :param save_directory: 保存图片的目录
    :param file_name: 保存图片的文件名，如果未指定则使用 URL 中的文件名
    """
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # 如果请求失败则抛出异常
            
            # 获取图片的文件名
            if not file_name:
                file_name = os.path.basename(url)
            
            # 确保保存目录存在
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            
            # 拼接保存路径
            save_path = os.path.join(save_directory, file_name)
            
            # 将图片内容写入文件
            with open(save_path, 'wb') as file:
                file.write(await response.read())
            
            print(f"图片已成功下载并保存到: {save_path}")
    
    except aiohttp.ClientError as e:
        print(f"下载图片时发生错误: {e}")


async def async_task(image_urls, save_directory):
    """
    异步下载多张图片。
    
    :param image_urls: 图片 URL 列表
    :param save_directory: 保存图片的目录
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in image_urls:
            tasks.append(download_image(session, url, save_directory))
        
        await asyncio.gather(*tasks)

def crash_new(name):
        try:
            tweets = driver.find_elements(By.CSS_SELECTOR, "article")
            if len(tweets) == 0:
                return '', -1, []
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
                logging.debug(f"用户名: {username}")
                logging.debug(f"日期: {date}")
                logging.debug(f"推文内容: {tweet_text}")
                if video_duration:
                    logging.debug(f"视频时长: {video_duration}")
                logging.debug(f"评论数: {comments}")
                logging.debug(f"转推数: {retweets}")
                logging.debug(f"点赞数: {likes}")
                logging.debug(f"观看数: {views}")
                if image_urls:
                    logging.debug("图片URL:")
                    for url in image_urls:
                        logging.debug(url)

                logging.debug("-" * 40)
                return tweet_text, date, image_urls
        except NoSuchWindowException as error:
            logging.error("No such window: target window already closed.", exc_info=True)
            return '', -2, [] 
        except WebDriverException as error:
            logging.error("WebDriverException occurred.", exc_info=True)
        finally:
           return '', -1, [] 

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
    logging.debug("访问推特页面中.....")
    try:
        with open("./twitterUrl.txt", "r", encoding="utf-8") as file:
            for line in file:
                try:
                    driver.get(line)
                    logging.debug("准备爬取推文中.....")
                    time.sleep(4)
                    name = driver.find_elements(
                        By.XPATH,
                        '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]',
                    )
                    if not name[0].text:
                        continue

                    twitter_user = name[0].text
                    tweet_text, date, image_urls = crash_new(twitter_user)
                    if date == -1:
                        continue
                    elif date == -2:
                        break 
                    save_dir = os.path.join('./image/', twitter_user)
                    if not content_queue.contains(tweet_text):
                        content_queue.enqueue(tweet_text)
                    asyncio.run(async_task(image_urls, save_dir))

                except TimeoutException:
                    logging.error("Loading the page timed out.")
                    time.sleep(2)
                except NoSuchWindowException:
                    logging.error("The target window is already closed.")
                    break
                except WebDriverException as e:
                    logging.error(f"WebDriverException occurred: {e}", exc_info=True)  
                    break 
                except Exception as e:
                    logging.error(f"other error: {e.message}") 
                    time.sleep(2)
    except BaseException as error:
        logging.error("open file has a error, ", str(error))
