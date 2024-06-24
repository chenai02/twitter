from collections import deque
class FixedSizeQueue:
    def __init__(self, max_size, remove_on_full=True):
        self.max_size = max_size
        self.remove_on_full = remove_on_full
        self.queue = deque()
        self.set = set()

    def is_empty(self):
        return len(self.queue) == 0

    def is_full(self):
        return len(self.queue) == self.max_size

    def enqueue(self, item):
        if self.is_full():
            if self.remove_on_full:
                removed_item = self.queue.popleft()  # 删除队列的第一个元素
                self.set.remove(removed_item)  # 从set中删除元素
            else:
                raise Exception("Queue is full")
        self.queue.append(item)
        self.set.add(item)  # 将元素添加到set中

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Dequeue from an empty queue")
        item = self.queue.popleft()
        self.set.remove(item)  # 从set中删除元素
        return item

    def contains(self, item):
        return item in self.set

    def size(self):
        return len(self.queue)

    def printQ(self, debug=False):
        if debug:
            for index, item in enumerate(self.queue):
                print(f"Item {index}: {item}")

if __name__ == '__main__':
    q = FixedSizeQueue(max_size=10)
    q.enqueue("SpaceX_2024-06-25 06:38:01")
    q.enqueue("SpaceX_2024-06-25 06:38:02")
    if q.contains("SpaceX_2024-06-25 06:38:01"):
        print("Found")
    q.printQ(debug=True)

