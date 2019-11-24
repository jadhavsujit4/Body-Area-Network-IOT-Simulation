import ast
from flask import Flask, request
import pymongo
import json
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
my_client = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_client["local"]
my_collection = my_db["devices4"]


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/get_data', methods=['GET'])
def get_data():
    if request.method == 'GET':
        return_string = ''
        for x in my_collection.find():
            return_string += str(x) + '\n\n'
        return return_string


@app.route('/post_data', methods=['POST'])
def post_data():
    if request.method == 'POST':
        data = dict(request.form)
        for k in data:
            data = k
            break
        data = json.loads(data)
        return_string = ''
        arr = []
        for device in data:
            for timestamp in data[device]:
                inner_dict = {'device': device, 'timestamp': timestamp}
                return_string += device + ', ' + timestamp + ', '
                for k in data[device][timestamp]:
                    if data[device][timestamp][k] and k == 'warning':
                        return_string += '****' + (str(data[device][timestamp][k])).upper() + '****, '
                    else:
                        return_string += str(data[device][timestamp][k]) + ', '
                    inner_dict[k] = data[device][timestamp][k]
                return_string += '\n'
                arr.append(inner_dict)
        x = my_collection.insert_many(arr)
        print(return_string)
        return return_string


if __name__ == "__main__":
    # app.run()
    app.run(host='0.0.0.0')

































'''
{
  "device1": {
    "2019-11-18T23:31:16": {
      "topic": "Normal message",
      "warning": false,
      "data": 1.5e6
    },
    "2019-11-18T23:42:56": {
      "topic": "Normal message",
      "warning": false,
      "data": 1400000
    },
    "2019-11-18T23:45:02": {
      "topic": "Normal message",
      "warning": false,
      "data": 1520000
    }
  },
  "device2": {
    "2019-11-18T02:00:07": {
      "topic": "Backup message",
      "warning": false,
      "data": 1500000
    },
    "2019-11-18T03:00:21": {
      "topic": "Backup message",
      "warning": false,
      "data": 1400000
    }
  }
}
'''



