# 创建应用实例
from gevent import pywsgi
import logging
import sys

from wxcloudrun import app

# 启动Flask Web服务
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,  # 控制台打印的日志级别
                    filename='stdout',  # 将日志写入log_new.log文件中
                    filemode='w',  # 模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志 a是追加模式，默认如果不写的话，就是追加模式
                    format="%(asctime)s:%(levelname)s:%(name)s -- %(message)s", datefmt="%Y/%m/%d %H:%M:%S"  # 日志格式
                    )
    #app.run(host=sys.argv[1], port=sys.argv[2])
    server = pywsgi.WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()
