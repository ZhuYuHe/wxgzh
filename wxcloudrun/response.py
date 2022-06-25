import json

from flask import Response
import time
import datetime


def make_succ_empty_response():
    data = json.dumps({'code': 200, 'data': {}})
    return Response(data, mimetype='application/json')


def make_succ_response(data):
    data = json.dumps({'code': 0, 'data': data})
    return Response(data, mimetype='application/json')


def make_err_response(err_msg):
    data = json.dumps({'code': -1, 'errorMsg': err_msg})
    return Response(data, mimetype='application/json')

# 消息回复返回体
# 示例：{
#  "ToUserName": "用户OPENID",
#  "FromUserName": "公众号/小程序原始ID",
#  "CreateTime": "发送时间", // 整型，例如：1648014186
#  "MsgType": "text",
#  "Content": "文本消息"
#}
def make_text_suss_response(uid, pid, content):
    t = str(int(time.time()))
    dict = {'ToUserName': uid, 'FromUserName': pid, 'CreateTime': t, 'MsgType': 'text', 'Content': content}
    data = bytes(json.dumps(dict, ensure_ascii=False), encoding='utf-8')
    return Response(data, mimetype='application/json')
