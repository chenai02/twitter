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

    def contains(self, item):
        """检查队列中是否包含某个元素。
        
        Args:
            item: 要检查的元素，可以是队列存储的任何类型。

        Returns:
            bool: 如果队列包含该元素则返回True，否则返回False。
        """
        return any(queued_item == item for queued_item in self.queue)
    
    def printQ(self):
        """以更易读的方式打印队列中的所有元素。"""
        for index, item in enumerate(self.queue):
            print(f"Item {index}: {item}")
