from datetime import datetime
from flask import render_template, request
import logging
from run import app
from wxcloudrun.dao import delete_counterbyid, query_counterbyid, insert_counter, update_counterbyid
from wxcloudrun.model import Counters
from wxcloudrun.response import make_succ_empty_response, make_succ_response, make_err_response, make_text_suss_response
from wxcloudrun.stock import StockUpdater

stockU = StockUpdater()

@app.route('/')
def index():
    """
    :return: 返回index页面
    """
    return render_template('index.html')

@app.route('/api/stock_price', methods=['POST'])
def get_price():
    """
    获取价格和买卖点
    输入结构示例:
    {
      "ToUserName": "gh_919b00572d95", // 小程序/公众号的原始ID，资源复用配置多个时可以区别消息是给谁的
      "FromUserName": "oVneZ57wJnV-ObtCiGv26PRrOz2g", // 该小程序/公众号的用户身份openid
      "CreateTime": 1651049934, // 消息时间
      "MsgType": "text", // 消息类型
      "Content": "回复文本", // 消息内容
      "MsgId": 23637352235060880 // 唯一消息ID，可能发送多个重复消息，需要注意用此 ID 去重
    }
    消息推送配置检查体:
    {
      "action": "CheckContainerPath"
    }
    """
    params = request.get_json()
    logging.info("params : {}".format(params))

    # 检查消息类型和内容
    if 'action' in params :
        return make_succ_empty_response()

    if params['MsgType'] != 'text' or params['Content'].strip() != '1':
        return make_err_response('action参数错误')

    uid = params['FromUserName']
    pid = params['ToUserName']
    content = stockU.get_stock_price()

    return make_text_suss_response(uid, pid, content)

@app.route('/api/count', methods=['POST'])
def count():
    """
    :return:计数结果/清除结果
    """

    # 获取请求体参数
    params = request.get_json()
    print(params)

    # 检查action参数
    if 'action' not in params:
        return make_err_response('缺少action参数')

    # 按照不同的action的值，进行不同的操作
    action = params['action']

    # 执行自增操作
    if action == 'inc':
        counter = query_counterbyid(1)
        if counter is None:
            counter = Counters()
            counter.id = 1
            counter.count = 1
            counter.created_at = datetime.now()
            counter.updated_at = datetime.now()
            insert_counter(counter)
        else:
            counter.id = 1
            counter.count += 1
            counter.updated_at = datetime.now()
            update_counterbyid(counter)
        return make_succ_response(counter.count)

    # 执行清0操作
    elif action == 'clear':
        delete_counterbyid(1)
        return make_succ_empty_response()

    # action参数错误
    else:
        return make_err_response('action参数错误')


@app.route('/api/count', methods=['GET'])
def get_count():
    """
    :return: 计数的值
    """
    counter = Counters.query.filter(Counters.id == 1).first()
    return make_succ_response(0) if counter is None else make_succ_response(counter.count)
