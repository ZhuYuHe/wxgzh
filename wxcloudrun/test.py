
import requests
import re
import efinance as ef

if __name__ == '__main__':
    #l = r.text.split('\n')
    #t = '港元兑换人民币'
    #l = [x for x in l if t in x]
    #text = l[0].split('title')[0].split('人民币')[0].strip()[-6:]
    #print(text)
    #r = requests.get("https://www.boc.cn/sourcedb/whpj/index.html")
    #r.encoding = 'utf-8'
    #html = r.text 
    #idx = html.index('<td>港币</td>')
    #html = html[idx:idx+300]
    #result = re.findall('<td>(.*?)</td>', html)
    #print(html)

    df = ef.stock.get_latest_quote(['600519', '00700', '200596'])
    print(df)
    print(df.columns)
    #df = df[['名称', '总市值', '更新时间']]
    #print(len(df))
    #t = df.iloc[0, 2]


