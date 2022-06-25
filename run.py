# 创建应用实例
from gevent import pywsgi
import sys

from wxcloudrun import app

# 启动Flask Web服务
if __name__ == '__main__':
    #app.run(host=sys.argv[1], port=sys.argv[2])
    server = pywsgi.WSGIServer((sys.argv[1], int(sys.argv[2])), app)
    server.serve_forever()
