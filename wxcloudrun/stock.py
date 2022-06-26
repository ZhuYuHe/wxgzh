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
'002415']
ideal_values = \
[36000.0,
15000.0,
2100.0,
830.0,
500.0,
1225.0,
4000.0,
3120.0]

hk_stock = {"腾讯控股", "古井贡B"}
hk_stock = {'00700', '200596'}

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

    def get_stock_price(self):
        now = int(time.time())
        if self.content != "" and not self.is_trans_time():
            return self.content
        if self.content == "" or now - self.content_uptime >= stock_uptime * 60:
            self.update_content()
        return self.content

    def update_content(self):
        now = int(time.time())
        if self.ex_rate <= 0 or now - self.ex_rate_uptime > 43200:
            self.update_ex_rate()
        text = [] 
        text.append("今日汇率1港币={}人民币\n".format(self.ex_rate))
        text.append("  名称     |理想市值|目前市值| 距离")
        sd = []
        df = ef.stock.get_latest_quote(stock_list)
        df = df[['代码', '名称', '总市值', '更新时间']]
        df['总市值'] /= 100000000
        df['总市值'] = df['总市值'].astype(int)
        self.content_time_str = str(df.iloc[0,3])
        for i in range(len(df)):
            stock_code = df.iloc[i, 0]
            stock_name = df.iloc[i, 1]
            market_value = df.iloc[i, 2]
            if stock_code in hk_stock:
                market_value *= self.ex_rate
            ideal_value = ideal_values[i]
            dis = (market_value - ideal_value) / market_value
            txt = "{0:<4}|{1:<{4}}|{2:<{5}}|{3:>4}%".\
                format(stock_name, int(ideal_value), int(market_value), \
                    int(dis*100), 13-len(str(int(ideal_value))), 13-len(str(int(market_value))))
            sd.append((txt, dis))
        sd = sorted(sd, key=lambda x: x[1])
        for i in sd:
            txt, dis = i
            text.append(txt)
        text.append("\n")
        text.append("汇率更新时间: {}".format(self.ex_rate_time_str))
        text.append("市值更新时间: {}".format(self.content_time_str))
        self.content = '\n'.join(text)
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
    print(stock_up.get_stock_price())