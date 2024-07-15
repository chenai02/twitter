import json, os, sys
import aiohttp
import asyncio
import aiofiles
from loguru import logger
from src.BaseData.BaseData import MessageData

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# 将 src 目录添加到 sys.path

sys.path.append(parent_dir)
from src.BaseData import *


async def get_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": app_id,
        "app_secret": app_secret
    })
    headers = {
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            response_json = await response.json()
            return response_json['tenant_access_token']


async def uploadImage(app_id, app_secret, image, retries=3):
    token = await get_token(app_id, app_secret)
    if retries < 0:
        logger.info("Max retries exceeded.")
        return None

    url = "https://open.feishu.cn/open-apis/im/v1/images"
    payload = {'image_type': 'message'}

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    async with aiofiles.open(image, 'rb') as f:
        image_data = await f.read()

    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('image', image_data, filename='12345.png', content_type='application/octet-stream')
        data.add_field('image_type', payload['image_type'])

        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                response_json = await response.json()
                return response_json['data']['image_key']
            else:
                return await uploadImage(app_id, app_secret, image, retries - 1)


async def sendMsg(message, robotToken):
    """
    通过异步方式向飞书发送文本消息
    :param message: 消息内容
    :param robotToken: 机器人Token
    """
    url = f"https://open.feishu.cn/open-apis/bot/v2/hook/{robotToken}"
    headers = {'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(message)):# 飞书机器人只能1s发送3条消息
            await asyncio.sleep(0.35)


async def sendMessageGroup(message, robotTokenList):
    tasks = []
    for token in robotTokenList:
        task = asyncio.create_task(sendMsg(message, token))  # 为每个token创建发送任务
        tasks.append(task)
    await asyncio.gather(*tasks)


async def sendMarkdownMsgNoImage(msg: MessageData):
    """
    发送富文本格式消息，但是没有图片格式
    :param message:
    :param robotTokenList:
    :param imagefile:
    :param href:
    :return:
    """

    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": msg.title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": msg.content,
                            },
                        ],
                        [
                            {
                                "tag": "text",
                                "text": msg.time
                            },
                            {
                                "tag": "a",
                                "text": "详情",
                                "href": msg.href
                            }
                        ],
                    ]
                },
            }
        },
    }
    await sendMessageGroup(message, msg.web_hook_List)


async def sendMarkdownMsg(msg: MessageData):
    """
    发送富文本格式消息
    :param message:
    :param robotTokenList:
    :param imagefile:
    :param href:
    :return:
    """
    image_key = await uploadImage(msg.app_id, msg.app_secret, msg.image_file)
    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": msg.title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": msg.content,
                            },
                        ],
                        [{
                            "tag": "img",
                            "image_key": image_key
                        }],
                        [
                            {
                                "tag": "text",
                                "text": msg.time
                            },
                            {
                                "tag": "a",
                                "text": "详情",
                                "href": msg.href
                            }
                        ],
                    ]
                },
            }
        },
    }
    await sendMessageGroup(message, msg.web_hook_List)

async def sendTextMsg(msg: MessageData):
    """
    发送文本消息
    :param msg:
    :return:
    """
    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": msg.title,
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": msg.content,
                            },
                        ],
                        [
                            {
                                "tag": "text",
                                "text": msg.time
                            },
                        ],
                    ]
                },
            }
        },
    }
    await sendMessageGroup(message, msg.web_hook_List)


async def sendBasicMsg(msg: MessageData):
    """
    发送文本消息，标题为没有加粗
    :param msg:
    :return:
    """
    message = {
        "msg_type": "text",
        "content": {
            "text": f"[{msg.title}]\n{msg.content}\n{msg.time}"
        }
    }
    await sendMessageGroup(message, msg.web_hook_List)



def feishu_test_func():
    robotToken = ["b9d43cf2-83b5-419a-a2a5-667ccb93da2d",
                  "17364265-5c64-444d-8ae2-325bf5084ccd"]
    image = "xxxxx"
    app_id = 'xxxx'
    app_secret = 'xxxxx'
    message = MessageData(robotToken, '[推特: 马斯克]', '推文内容: Everyday Astronaut interview and Starship factory tour!', '20240622-15:09:31', '123.com', image, app_id, app_secret)
    asyncio.run(sendMarkdownMsgNoImage(message))

if __name__ == '__main__':
    feishu_test_func()