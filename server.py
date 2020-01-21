import flask

from pos_ner import get_pos_ner

def process(data):
    request_type = list(data.keys())[0]
    sentence = data[request_type]
    if request_type == 'pos_ner':
        return get_pos_ner(sentence)
    elif request_type == 'addr_format':
        pass
    elif request_type == 'workOrder_filter':
        pass
    else:
        return 'You have requested error request_type'


# 引入Flask类，Flask类实现了一个WSGI应用
app = flask.Flask(__name__)
# 使用app.route装饰器会将URL和执行的视图函数的关系保存到app.url_map属性上。
# 处理URL和视图函数的关系的程序就是路由，这里的视图函数就是下面对应的函数
@app.route("/", methods=["POST"])
def main():
    if flask.request.method == "POST":
        data = flask.request.form
        response_data = process(data)
        return response_data


if __name__ == '__main__':
    # app.run(host='127.0.0.1', port='8006')
    app.run(host='0.0.0.0', port='8006')


