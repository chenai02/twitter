# -*- coding: utf-8 -*-
#
# BaseData.py
# Created by 90323 on 2024/6/22.
#
# 

""""""
from dataclasses import dataclass

@dataclass
class MessageData:
    web_hook_List: list
    title: str
    content: str
    time: str
    href: str = None
    image_file: str = None
    app_id: str = None
    app_secret: str = None


if __name__ == '__main__':
    messageData = MessageData('111', '222', '333', '4444')
    print(messageData)