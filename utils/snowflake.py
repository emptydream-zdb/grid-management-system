import time

class Snowflake:
    def __init__(self, datacenter_id, worker_id):
        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1

    def generate_uuid(self):
        timestamp = int(time.time() * 1000)

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id.")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                timestamp = self.wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return ((timestamp - 1288834974657) << 22) | (self.datacenter_id << 17) | (self.worker_id << 12) | self.sequence

    def wait_next_millis(self, last_timestamp):
        timestamp = int(time.time() * 1000)
        while timestamp <= last_timestamp:
            timestamp = int(time.time() * 1000)
        return timestamp

# # Usage example
# snowflake = Snowflake(datacenter_id=0, worker_id=0)
# uuid = snowflake.generate_uuid()
# print(uuid)

'''
这段代码定义了一个名为 Snowflake 的类，该类用于生成全局唯一的 ID。
这种 ID 生成方式在 Twitter 等大型互联网公司中被广泛使用。

Snowflake 类的构造函数 __init__ 接收两个参数：datacenter_id 和
 worker_id。这两个参数分别代表数据中心的 ID 和工作机器的 ID，用于
 在分布式系统中区分不同的机器。此外，构造函数还初始化了两个属性：
 sequence 和 last_timestamp。sequence 用于记录同一毫秒内生成的 ID 数量，
 last_timestamp 用于记录最后一次生成 ID 的时间。

generate_uuid 方法是生成 ID 的主要逻辑。首先，它获取当前时间的毫秒级时间戳。
如果当前时间小于最后一次生成 ID 的时间，那么抛出异常，因为这可能意味着系统时钟
出现了问题。如果当前时间等于最后一次生成 ID 的时间，那么 sequence 加 1，然后
与 4095 进行与运算，这是为了确保 sequence 不会超过 4095。如果 sequence 已
经达到 4095，那么等待到下一个毫秒。如果当前时间大于最后一次生成 ID 的时间，那
么 sequence 重置为 0。最后，将各部分信息按照一定的位数进行移位和或运算，生成
最终的 ID。

wait_next_millis 方法用于等待到下一个毫秒。它不断获取当前时间，直到当前时间大
于传入的时间戳。

这段代码的主要目的是生成全局唯一的 ID，而且这些 ID 是按照时间顺序生成的，因此
可以用于排序。同时，通过将数据中心 ID 和工作机器 ID 包含在 ID 中，可以避免在
分布式系统中生成重复的 ID。
'''
