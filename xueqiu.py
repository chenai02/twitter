import requests, time, json, random
from collections import deque
from loguru import logger
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
            logger.info(f"Item {index}: {item}")

def sendMes(URL, message,debug = 0):
    if debug == 1:
        return
    for u in URL:
        payload_message = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", u, headers=headers, data=json.dumps(payload_message))
        while response.status_code != 200:
            response = requests.request("POST", u, headers=headers, data=json.dumps(payload_message))
            time.sleep(0.5)



def craw_xq(url, session):
    
    headers ={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}

    # 第一步,向雪球网首页发送一条请求,获取cookie
    response = session.get("https://xueqiu.com", headers=headers)
    # TODO 1 如果session失效，那么需要重新获取
    if response.status_code != 200:
        session = requests.Session()  # 重新创建session
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
        response = session.get("https://xueqiu.com", headers=headers)

    # 第二步,获取动态加载的新闻数据
    page_json = session.get(url=url,headers=headers).json()
    # 返回的json示例：
    #{'next_max_id': 3411397, 'items': [{'id': 3411433, 'text': '【ST聆达：子公司现有PERC型电池片产线经营性现金流紧张 预计在短期内无法恢复正常生产】ST聆达公告，截至本公告披露日，公司基本面未发
    # 生重大变化，公司子公司金寨嘉悦现有PERC型电池片产线经营性现金流紧张，预计在短期内无法恢复正常生产。公司正积极回收采购预付款并寻求融资渠道，包括但不限于接受低息无抵押财务资助、引介融资渠道 
    # 等方式。协调债务整体解决方案，引进外部资金，减轻债务负担，增强公司的抗风险能力，补充流动资金，改善公司的财务状况，尽快恢复子公司金寨嘉悦的生产经营。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292438159', 'created_at': 1717411308000, 'view_count': 0, 'status_id': 292438159, 'reply_count': 0, 'share_count': 1, 'sub_type': 0}, {'id': 3411431, 'text': '【江河集团： 
    # 全资子公司中标广华医院二期幕墙工程】江河集团公告，全资子公司香港江河幕墙工程有限公司近日收到广华医院二期幕墙工程中标通知书，中标金额约2.51亿港元，折合人民币约2.32亿元，约占公司2023年度营 
    # 业收入的1.11%。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292437791', 'created_at': 1717411146000, 'view_count': 0, 'status_id': 292437791, 'reply_count': 0, 'share_count': 0, 
    # 'sub_type': 0}, {'id': 3411426, 'text': '美国BD公司将以42亿美元现金收购EDWARDS的CRITICAL CARE部门。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292437500', 'created_at': 1717410941000, 'view_count': 0, 'status_id': 292437500, 'reply_count': 1, 'share_count': 0, 'sub_type': 0}, {'id': 3411420, 'text': '【ST阳光：控股股东阳光集团最近出现部分贷款逾期】ST阳光公告，公
    # 司股票于2024年5月30日、5月31日和6月3日连续3个交易日内日收盘价格跌幅偏离值累计达到12%，属于股票交易异常波动情形。公司控股股东阳光集团最近出现部分贷款逾期，对应金额为29,240.98万元，存在因债
    # 务问题而涉及诉讼的情况，目前阳光集团正积极与银行协商应对措施。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292437287', 'created_at': 1717410805000, 'view_count': 0, 'status_id': 
    # 292437287, 'reply_count': 0, 'share_count': 0, 'sub_type': 0}, {'id': 3411415, 'text': '【达实智能：子公司签署5823.33万元智慧医院项目合同】达实智能公告，公司于2024年4月2日披露了《关于智慧
    # 医院项目中标的公告》，近日，公司全资子公司江苏达实久信医疗科技有限公司与上海建工集团股份有限公司就上海交通大学医学院附属第九人民医院祝桥院区项目有关事项协商一致，在上海市正式签署了合同， 
    # 合同金额5823.33万元。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292436639', 'created_at': 1717410433000, 'view_count': 0, 'status_id': 292436639, 'reply_count': 0, 'share_count': 0, 'sub_type': 0}, {'id': 3411410, 'text': '【毕马威：AIGC正形成“数智”转型的新质生产力】国际四大会计师事务所之一的毕马威表示，新一轮人工智能发展浪潮中，生成式人工智能（AIGC）形成了“数 
    # 智”转型的新质生产力，并成为推动产业创新与经济高质量发展的新引擎。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292436470', 'created_at': 1717410333000, 'view_count': 0, 'status_id': 292436470, 'reply_count': 2, 'share_count': 0, 'sub_type': 0}, {'id': 3411409, 'text': '【亿帆医药：子公司获得间苯三酚注射液药品注册证书】亿帆医药公告，全资子公司合肥亿帆生物制药有限公
    # 司于2024年6月3日收到国家药品监督管理局核准签发的间苯三酚注射液《药品注册证书》。间苯三酚注射液适用于治疗消化道和胆道功能障碍引起的急性痉挛性疼痛等。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292436469', 'created_at': 1717410323000, 'view_count': 0, 'status_id': 292436469, 'reply_count': 0, 'share_count': 0, 'sub_type': 0}, {'id': 3411406, 'text': '【江铃汽车：5月销量同比增长10.6%】江铃汽车公告，5月汽车销量27210辆，同比增长10.6%，1-5月累计销量13.19万辆，同比增长10%。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292436326', 'created_at': 
    # 1717410241000, 'view_count': 0, 'status_id': 292436326, 'reply_count': 1, 'share_count': 0, 'sub_type': 0}, {'id': 3411403, 'text': '埃及总统府发言人3日说，埃及总统塞西接受总理马德布利提 
    # 交的内阁辞呈。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292436255', 'created_at': 1717410209000, 'view_count': 0, 'status_id': 292436255, 'reply_count': 0, 'share_count': 0, 'sub_type': 0}, {'id': 3411397, 'text': '【中创环保收年报问询函：要求说明近三年净利润持续亏损的原因】深交所向中创环保下发布年报问询函，要求说明近三年净利润持续亏损、各业务毛利率变化的主要 
    # 原因，是否存在冲回以前年度收入或补记以前年度成本的情形。', 'mark': 0, 'target': 'http://xueqiu.com/5124430882/292436057', 'created_at': 1717410106000, 'view_count': 0, 'status_id': 292436057, 'reply_count': 0, 'share_count': 1, 'sub_type': 0}], 'next_id': 3411393}

    return page_json['items']

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

if __name__=='__main__':

    # 从配置文件中加载配置
    config = load_config('./config/config.json')
    url = config.get('url')
    maxSize = config.get('maxSize')

    session = requests.Session()
    xq_id_queue = FixedSizeQueue(maxSize)

    while True:
        tmp = 0
        news = craw_xq(url,session)
        for n in news:
            if n['mark'] == 0:   # mark == 1 是重要的新闻
                # TODO 2 先看n['id']是否已经存在于xq_id_queue中，如果是，则continue。否则将n['id']存入xq_id_queue中，并且将n存入q中。在存入xq_id_queue以及q时，如果队列已满，则先dequeue，再用enqueue存入。
                if not xq_id_queue.contains(n['id']):  # 假设contains方法接受一个id并检查队列中是否存在
                    xq_id_queue.enqueue(n['id'])  # 假设enqueue方法存入id
                    print(n['text'])
        time.sleep(random.randint(5,8))