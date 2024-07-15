from src.Constant.Constant import Constant
from src.FixedSizeQueue.FixedSizeQueue import FixedSizeQueue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchWindowException
from dingtalkchatbot.chatbot import DingtalkChatbot
from src.Myfeishu import *
import pytz
from src.MyMQ.myMQ import *
from src.Twitter.Twitter import Twitter
from loguru import logger

# def load_config(config_path):
#     with open(config_path, 'r') as file:
#         config = json.load(file)
#     return config
#
#
# CONFIG = load_config('./user_config/config.json')
# USR_CFG = load_config('./user_config/usr_cfg.json')
# DD_webhook5_J = CONFIG.get('DD_webhook5_J')
# DD_secret5_J = CONFIG.get('DD_secret5_J')
# CONFIG = load_config('./user_config/config.json')
#
#
# def dingtalk5(msg, webhook5=DD_webhook5_J, secret5=DD_secret5_J):
#     xiaoding5 = DingtalkChatbot(webhook5, secret=secret5)  # 方式二：勾选“加签”选项时使用（v1.5以上新功能）
#     xiaoding5.send_text(msg=msg)
#
#
# def load_config(config_path):
#     with open(config_path, 'r') as file:
#         config = json.load(file)
#     return config


def init_chrome(url):
    # 初始化
    chrome_options = ChromeOptions()
    chrome_options.add_argument("window-position=660,0")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(5)


    try:
        driver.get(url)
    except TimeoutException:
        driver.execute_script("window.stop()")
    driver.set_page_load_timeout(60)
    return driver


# def send_to_feishu(twitter, url, uuid, date, tweet_text):
#     try:
#         usr = USR_CFG.get("Twitte_Usr").get(url)
#     except Exception as e:
#         usr = ""
#     mess = f"{date}  " + f"{url.split('/')[-1]}:" + f"{tweet_text}"
#     print(mess)
#     twitter.content_queue.enqueue(uuid)
#     print(uuid)
#     if "Reuters Business" in uuid:
#         twitter.content_queue.printQ(debug=True)
#     dingtalk5(mess)
#     mess = MessageData(CONFIG.get("feishu_news"), f"[推特: {usr}]", f"推文内容: {tweet_text}", date,
#                        url)
#     asyncio.run(sendMarkdownMsgNoImage(mess))
#     x_type = CONFIG.get('X_news').get('x_type')
#     x_mq_name = CONFIG.get('X_news').get('x_mq_name')
#     x_Qkey = CONFIG.get('X_news').get('x_Qkey')
#     message_body = MessageBody(
#         msg_type=x_type,
#         title=f"[推特: {usr}]",
#         content=tweet_text,
#         QKey=x_Qkey,
#         links=url,
#         create_time=date
#     )
#     twitter.my_mq.publish_message(x_mq_name, message_body.to_json())


if __name__ == "__main__":
    string_list = []
    driver = init_chrome(Constant.login_url)
    # 设置cookie
    logger.info("设置cookie中.....")
    cookies = json.load(open("123.json", "r"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    CONFIG = []
    twitter = Twitter(100, CONFIG, driver)
    # path = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[2]/div[1]/div/div[1]/div/div/span/span[1]'

    logger.info("访问推特页面中.....")
    # 第一次爬取时，只需要爬一条消息
    count = 0
    currentTime = datetime.now().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Shanghai"))
    # # 创建一个自定义的日期和时间
    # custom_time = datetime(2023, 7, 6, 15, 30, 0)
    #
    # # 将这个时间设置为UTC时区
    # custom_time_utc = custom_time.replace(tzinfo=pytz.UTC)
    #
    # # 转换为上海时区
    # currentTime = custom_time_utc.astimezone(pytz.timezone("Asia/Shanghai"))

    while True:
        try:
            with open(Constant.twitter_url_path, "r", encoding="utf-8") as file:
                for line in file:
                    try:
                        url, twitter_user = twitter.find_elements(line, By.XPATH, Constant.element_path)
                        if url == -1:
                            continue
                        tweet_text, date, image_urls, uuid = twitter.crash_new(twitter_user, currentTime)
                        time.sleep(15)
                        if date == '-1':
                            continue
                        elif date == '-2':
                            break
                        # send_to_feishu(twitter, url, uuid, date, tweet_text)
                    except TimeoutException:
                        logger.error("Loading the page timed out.")
                        time.sleep(15)
                    except NoSuchWindowException:
                        logger.error("The target window is already closed.")
                        break
                    except WebDriverException as e:
                        logger.error(f"WebDriverException occurred: {e}")
                        time.sleep(15)
                        continue
                    except Exception as e:
                        logger.error(f"other error: {e}")
                        time.sleep(20)
        except BaseException as error:
            logger.error("open file has a error, ", str(error))
        count = 1
        time.sleep(300)
