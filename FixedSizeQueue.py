from collections import deque
class FixedSizeQueue:
    def __init__(self, max_size):
        self.max_size = max_size
        self.queue = deque()

    def is_empty(self):
        return len(self.queue) == 0

    def is_full(self):
        return len(self.queue) == self.max_size

    def enqueue(self, item):
        if self.is_full():
            # 可以选择抛出异常、打印警告或删除队列中的第一个元素（类似于循环队列）
            self.queue.popleft()  # 删除队列的第一个元素
        self.queue.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from an empty queue")
        return self.queue.popleft()

    def contains(self, item):
        return item in self.queue

    def size(self):
        return len(self.queue)

    
    def printQ(self):
        """以更易读的方式打印队列中的所有元素。"""
        for index, item in enumerate(self.queue):
            print(f"Item {index}: {item}")
