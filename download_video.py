import os
import threading
import requests


max_connections = 3  # 定义最大线程数,可根据网速修改
pool_sema = threading.BoundedSemaphore(max_connections)  # 或使用Semaphore方法


def get_url_video(srcs, len, name):
    thread_list = []
    for src in srcs:
        t = threading.Thread(target=download_video, args=(src, len, name), name=f'{src[37:50]}')
        len -= 1
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()  # 子线程调用join()方法，使主线程等待子线程运行完毕之后才退出


def download_video(src, len, name):
    pool_sema.acquire()  # 加锁，限制线程数
    image_name = f'{len}' + '_' + src.split("/")[-1].split("?")[0]
    image_path = os.path.join(name, image_name)

    if os.path.exists(image_path):
        print(f'{image_name} already exists.')
        pool_sema.release()  # 解锁
        return

    print(f'{image_name} is downloading')

    while True:
        try:
            response = requests.get(src)
            if response.status_code == 200:
                with requests.get(src, stream=True) as r:
                    with open(image_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                break  # 如果状态码为200，跳出循环
        except requests.exceptions.RequestException:
            print("发生错误:重新连接")

    pool_sema.release()
