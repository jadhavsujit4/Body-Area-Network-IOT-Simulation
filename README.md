# Body-Area-Network-IOT-Simulation
Scalable Computing Project-4(Trinity College Dublin)

# Team 1 Code

## Overview
 
There are three files, _devices.py_ simulates a series of devices within the body, _sink.py_ acts as a sink, receiving and actuating from the messages it receives from _devices.py_. A server API is implemented in _server.py_ which the sink sends to as appropriate.

## Body code

Python 3.7.4 is required, as well as _Scipy 1.3.1_. If the sink is running from a remote IP address and not localhost, the new IP address needs to be put in as appropriate in line 46 (line 48 should not be changed).

While the sink is running ready to receive messages, run _devices.py_ as follows:
```shell
python3 devices.py
```

## Sink code

Setup instructions:
- Installing the latest stable version on node-js on a linux VM
- Using the NPM package manager to install 'axios' & 'dgram' packages
- Remove any firewalls on the port 2356
- Run the script using node to listen to UDP packets from device

## Server code

Configure mongoDb and get the server running on localhost:27017
Setup python3 along with pip3

To install dependencies:
```shell
	sudo pip3 install flask
	sudo pip3 install pymongo
```

Run the command: ```python3 server.py```

The server will run on localhost:5000
The device data can be pushed on the server using POST request on http://localhost:5000/post_data
The device data can be retrieved from the server using GET request on http://localhost:5000/get_data

