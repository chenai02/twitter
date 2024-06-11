import threading

def process_data(data, thread_id):
    # 这里可以添加处理数据的逻辑
    print(f"Thread {thread_id}: Processing data... Length of data is {data}\n")


def create_thread(data, num_threads_count):
    def worker(data, thread_id):
        process_data(data, thread_id)

    return threading.Thread(target=worker, args=(data, num_threads_count))


def main(file_path):
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


if __name__ == "__main__":
    file_path = "./twitterUrl.txt"
    main(file_path)
