import logging
import time
import datetime
import efinance as ef
import requests

stock_list = \
{
    "腾讯控股" : ["00700", 96.22, 36000.0],
    "贵州茅台" : ["600519", 12.56, 15000.0],
    "洋河股份" : ["002304", 15.07, 2100.0],
    "分众传媒" : ["002027", 144.42, 830.0],
    "古井贡B" : ["200596", 5.29, 500.0],
    "陕西煤业" : ["601225", 96.95, 1225.0],
    "美的集团" : ["000333", 69.97, 4000.0],
    "海康威视" : ["002415", 94.33, 3120.0]
}

hk_stock = {"腾讯控股", "古井贡B"}

# 更新时间 5 分钟
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
        self.ex_rate = 0.8523
        self.ex_rate_uptime = int(time.time())

    def get_stock_price(self):
        now = int(time.time())
        if self.content != "" and not self.is_trans_time():
            return self.content
        if self.content == "" or now - self.content_uptime >= 300:
            self.update_content()
        return self.content

    def update_content(self):
        now = int(time.time())
        if now - self.ex_rate_uptime > 86400:
            self.update_ex_rate()
        text = [] 
        text.append("今日汇率1港币={}人民币\n".format(self.ex_rate))
        text.append("  名称     |理想市值|目前市值| 距离")
        sd = []
        for stock, l in stock_list.items():
            stock_code = l[0]
            guben = l[1]
            ideal_value = l[2]
            df = ef.stock.get_quote_history(stock_code, klt=stock_uptime)
            stock_price = df.iloc[-1, 4]
            market_value = guben * stock_price
            if stock in hk_stock:
                market_value *= self.ex_rate
            dis = (market_value - ideal_value) / market_value
            if stock == "古井贡B":
                stock = "古井贡B "
            txt = "{0:<4}|{1:<{4}}|{2:<{5}}|{3:>4}%".\
                format(stock, int(ideal_value), int(market_value), \
                    int(dis*100), 13-len(str(int(ideal_value))), 13-len(str(int(market_value))))
            sd.append((txt, dis))
        sd = sorted(sd, key=lambda x: x[1])
        for i in sd:
            txt, dis = i
            text.append(txt)
        self.content = '\n'.join(text)
        self.content_uptime = int(time.time())

    def update_ex_rate(self):
        r = requests.get("http://hl.anseo.cn/")
        l = r.text.split('\n')
        t = '港元兑换人民币'
        l = [x for x in l if t in x]
        text = l[0].split('title')[0].split('人民币')[0].strip()[-6:]
        self.ex_rate = float(text)
        self.ex_rate_uptime = int(time.time())

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