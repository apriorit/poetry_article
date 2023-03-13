import os
from discount_calculator.calculator import random_discount
import flask

app = flask.Flask(__name__)


@app.route('/api/order')
def create_order():
    discount = random_discount()
    return f'Order created, discount is {discount}.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=os.getenv('ORDER_MANAGER_PORT'))
