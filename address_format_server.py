import flask

from address_format import addrFormat

def process(data):
    sentence = data.get('sentence')
    town = data.get('town')
    response = addrFormat.addr_format(sentence, town)

    response['orderId'] = data.get('orderId')
    return response


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
    # app.run(host='127.0.0.1', port='6061',threaded=True)
    app.run(host='172.16.0.119', port='6061',threaded=True)


