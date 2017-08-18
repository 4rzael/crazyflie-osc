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

* [ ] Unit tests

* [x] Sphinx documentation

## How to install :

### LINUX :

* install git, python3, pip3
* install virtualenv (pip package)
* clone this repository
* create a new virtualenv and activate it
* install python dependencies `pip3 install -r requirements`

### WINDOWS :

#### NOTE : You don't need to clone this repository or anything, the script will take care of this.
* download [this file](https://gist.github.com/4rzael/b65ba5880ff7d0c1106d8b3dc9d719ca#file-install-crazyflie-osc-bat) as a .bat file
* run it as admin. (If they ask you things and you don't know what to do, use the defaults)
* install the crazyradio drivers :
  * plug in the radio
  * run zadig (win+r, then type zadig, then enter)
  * select the crazyradio and click on "install driver"

## How to run :

### LINUX :

* run the server `cd src; ./server.py`

### WINDOWS :

* run the file name `run.bat`

## How to test :

### NEW WAY :

In order to use (or manually test) this project, you should use [my Unity3D client](https://github.com/4rzael/crazyflie-osc-unity).

### OLD WAY :

No unit tests are currently present, but manual test client and server are present.

* run both of them : `cd manual_tests; ./test_client.py` and `cd manual_tests; ./test_server.py`

* write commands in the test_client console.

* alternatively, you can run `./test_client.py --file full_run.py` in order to execute a pre-planned connection (you will need changes in order to accomodate to your setup)
