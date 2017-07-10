# crazyflie-osc
An OSC server to control crazyflies

#### NOTE : OSC documentation in the [project wiki](https://github.com/4rzael/crazyflie-osc/wiki)

## Functionalities :

* [x] Drone connection

* [x] Sending 3D position setpoints

* [x] LPS configuration

* [x] Drone param system

* [x] Drone logging system

* [ ] OSC debugging system

* [ ] Unit test

* [x] Sphinx documentation

## How to run :

* create a new virtualenv

* install python dependencies `pip3 install -r requirements`

* run the server `cd src; ./server.py`

## How to test :

No unit tests are currently present, but manual test client and server are present.

* run both of them : `cd manual_tests; ./test_client.py` and `cd manual_tests; ./test_server.py`

* write commands in the test_client console.

* alternatively, you can run `./test_client.py --file full_run.py` in order to execute a pre-planned connection (you will need changes in order to accomodate to your setup)
