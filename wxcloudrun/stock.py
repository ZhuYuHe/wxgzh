import json
import logging
import time
import datetime
import efinance as ef
import re
import requests

stock_list = \
['00700',
# 茅台
'600519',
# 洋河
'002304',
# 分众
'002027',
# 古B
'200596',
# 陕煤
'601225',
# 美的
'000333',
# 海康
'002415',
# 福寿园
'01448']
nick_names = \
[
"企鹅",
"小茅",
"小羊",
"小分",
"小古",
"小陕",
"小美",
"小海",
"小福",
]
ideal_values = \
[
    28500.0,
    16500.0,
    2100.0,
    790.0,
    660.0,
    1350.0,
    4000.0,
    3120.0,
    110.0
]

sold_values = \
[
    66000.0,
    37000.0,
    5500.0,
    1850.0,
    1440.0,
    2860.0,
    12000.0,
    8400.0,
    330.0
]

#hk_stock = {"腾讯控股", "古井贡B"}
hk_stock = {'00700', '200596', '01448'}

# 更新时间 2 分钟
stock_uptime = 5

#class Info(db.Model):
#    __tablename__ = 'Info'
#    id = db.Column(db.Integer, primary_key=True)
#    content = db.Column('content', db.String(1024))
#    created_at = db.Column('createAt', db.Integer)
#    updated_at = db.Column('updatedAt', db.Integer)


class StockUpdater():
    
    def __init__(self):
        self.content = ""
        self.content_uptime = int(time.time())
        self.content_time_str = "2022-06-24 16:08:00"
        self.ex_rate = 0.0
        self.ex_rate_uptime = int(time.time())
        self.ex_rate_time_str = "2022-06-26 10:30:00"
        self.value_content = ""
        self.mini_programe_content = {}

    def get_content_by_mod(self, mode = 1):
        if mode == 1:
            return self.content
        elif mode == 2:
            return self.value_content
        elif mode == 3:
            return self.mini_programe_content

    def get_stock_price(self, mod=1):
        now = int(time.time())
        if self.content != "" and not self.is_trans_time():
            if int(self.content_time_str[11:13]) < 16:
                self.update_content()
            return self.get_content_by_mod(mod)

        if self.content == "" or now - self.content_uptime >= stock_uptime * 60:
            self.update_content()
        
        return self.get_content_by_mod(mod)

    def update_content(self):
        now = int(time.time())
        if self.ex_rate <= 0 or now - self.ex_rate_uptime > 43200:
            self.update_ex_rate()
        text = [] 
        text2 = []
        mini_data = []
        #text.append("   名称    |理想市值|目前市值| 距离")
        text.append("   名称     |距买点距离|距卖点距离")
        text2.append("   名称     |买点|当前市值|卖点")
        sd = []
        df = ef.stock.get_latest_quote(stock_list)
        df = df[['代码', '名称', '总市值', '更新时间']]
        df['总市值'] /= 100000000
        df['总市值'] = df['总市值'].astype(int)
        tencent_time = str(df.iloc[0,3])
        maotai_time = str(df.iloc[1,3])
        #self.content_time_str = str(df.iloc[0,3])
        self.content_time_str = tencent_time if tencent_time >= maotai_time else maotai_time
        for i in range(len(df)):
            stock_code = df.iloc[i, 0]
            stock_name = df.iloc[i, 1]
            market_value = df.iloc[i, 2]
            if stock_code in hk_stock:
                market_value *= self.ex_rate
            ideal_value = ideal_values[i]
            sold_value = sold_values[i]
            nick_name = nick_names[i]
            dis = (market_value - ideal_value) / market_value
            sold_dis = 0
            sold_dis = (sold_value - market_value) / market_value
            mini_item = {"name": nick_name, "idealValue": int(ideal_value), "marketValue": int(market_value),
                         "soldValue": int(sold_value), "idealDis": str(int(dis*100))+'%', "soldDis": str(int(sold_dis*100))+'%'}
            mini_data.append((mini_item, int(dis*100)))
            if stock_name == '福寿园':
                stock_name = '福寿园' + chr(0x3000) + ' '
            txt = "{0:<3}|{1:>10}% |{2:>10}%".\
                format(stock_name, int(dis*100), int(sold_dis*100))
            txt2 = "{0:<3}|{1:>5}|{2:>5}|{3:>5}".\
                format(stock_name, int(ideal_value), int(market_value), int(sold_value))
            sd.append((txt, dis))
            text2.append(txt2)
        sd = sorted(sd, key=lambda x: x[1])
        mini_data = sorted(mini_data, key=lambda x : x[1])
        mini_data = [x[0] for x in mini_data]
        self.mini_programe_content = {"update_time": self.content_time_str, "data": mini_data}
        for i in sd:
            txt, dis = i
            text.append(txt)

        text.append("\n1港币={}人民币\n".format(self.ex_rate))
        text.append("市值更新时间: {}".format(self.content_time_str))
        text.append("汇率更新时间: {}".format(self.ex_rate_time_str))
        text.append("\n备注：距离=(当前市值-买/卖点)/当前市值")
        text.append("发送 2 查看买/卖点市值与当前市值")
        text2.append("\n1港币={}人民币\n".format(self.ex_rate))
        text2.append("市值更新时间: {}".format(self.content_time_str))
        text2.append("汇率更新时间: {}".format(self.ex_rate_time_str))
        text2.append("\n备注: 发送 1 查看当前市值与买卖点距离")

        self.content = '\n'.join(text)
        self.value_content = '\n'.join(text2)
        self.content_uptime = int(time.time())
        logging.info("update content at {}".format(self.content_time_str))

    def update_ex_rate(self):
        r = requests.get("https://www.boc.cn/sourcedb/whpj/index.html")
        r.encoding = 'utf-8'
        html = r.text 
        idx = html.index('<td>港币</td>')
        html = html[idx:idx+300]
        result = re.findall('<td>(.*?)</td>', html)[-1]
        self.ex_rate = round(float(result) / 100, 4)
        self.ex_rate_uptime = int(time.time())
        self.ex_rate_time_str = str(datetime.datetime.now())[:19]
        logging.info("update ex_rate at {}".format(self.ex_rate_uptime))

    def is_trans_time(self):
        time = datetime.datetime.now()
        weekday = time.weekday()+1
        hour = time.hour
        if weekday < 6 and ((hour >= 9 and hour <= 12) or (hour >= 13 and hour <= 16)):
            return True
        return False

if __name__ == '__main__':
    stock_up = StockUpdater()
    dict = {'code': 200, 'data': stock_up.get_stock_price(3)}
    print(json.dumps(dict, ensure_ascii=False))
    #data = bytes(json.dumps(dict, ensure_ascii=False), encoding='utf-8')
    #print(data)
