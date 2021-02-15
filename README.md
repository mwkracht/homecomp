# Traffic Simulator

[![Build Status](https://travis-ci.org/mwkracht/homecomp.svg?branch=master)](https://travis-ci.org/mwkracht/homecomp)
[![Coverage Status](https://coveralls.io/repos/github/mwkracht/homecomp/badge.svg?branch=master)](https://coveralls.io/github/mwkracht/homecomp?branch=master)

This code originated as a coding project for an interview. Currently, it is only being mainatined it as an example python project that can be used to get other python projects off the ground faster. I will continue to incorporate any useful patterns for python packaging (i.e. how to run tests, hook into CI builds, setup logging, handle init importing, etc.) as I run across them.

The package should generally work but the code content is not going to be expanded. Test coverage will not be expanded either unless it provides an opportunity to show a useful testing pattern.

#### Usage Instructions

Provided is a trafficsim command line utility (traffic-simulator) that will all for the running of simple one traffic light simulations. The usage of that script follow:

```shell
usage: traffic-simulator [-h] red_ms yellow_ms green_ms [step]

Run Simple Traffic Signal Simulator. To safely exit the simulation press 'q'.

positional arguments:
  red_ms      Duration in ms for red light
  yellow_ms   Duration in ms for yellow light
  green_ms    Duration in ms for green light
  step        Duration in ms for simulation step. Defaults to 100ms

optional arguments:
  -h, --help  show this help message and exit
```

This simulator will run indefinitely until a user safely exits by pressing the 'q' key. The trafficsim package will need to be installed prior to running the traffic-simulator script.

An example usage of the traffic-simulator utility for a traffic light sim where each light cycles every second:

```shell
traffic-simulator 1000 1000 1000
```

#### Package Installation

Use pip to install this repository.

```shell
git clone git@github.com:mwkracht/trafficsim.git
pip install trafficsim
```

#### Running Tests

All tests and linting is run using tox. Tox can be installed using pip.

```shell
tox -c <path to trafficsim>/tox.ini
```

