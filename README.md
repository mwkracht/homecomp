# Home Buying Comparison Tool

[![Build Status](https://travis-ci.org/mwkracht/homecomp.svg?branch=master)](https://travis-ci.org/mwkracht/homecomp)
[![Coverage Status](https://coveralls.io/repos/github/mwkracht/homecomp/badge.svg?branch=master)](https://coveralls.io/github/mwkracht/homecomp?branch=master)

This project was created in order to compare value over time between buying (or renting) different
properties. There are a lot of existing buy vs. rent calculators available but it is much harder
to come by a tool for comparing the value of buying different properties.

The tool will give a projection over time of the impact of buying a certain home will have on your
networth assuming you have a fixed monthly housing budget and a lump sum of cash available for any
down payment.

This tool is proabably not useful if most housing options are relativey similar. In Washington DC
housing options vary widely from row homes with no HOAs, to condo units with HOAs into the 1k+
range, and rental options which is what drove the creation of this tool.

#### Usage

The package will install a command line utilty which can be used to model different housing options:

```shell
Usage: homecomp [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  buy   Subset of simulations available for buying housing
  rent  Subset of simulations available for renting housing
```

#### Package Installation

Use pip to install this repository.

```shell
pip install homecomp
```

If developing, run the following command in the base repository directory:

```shell
pip install -e .
```

#### Running Tests

All tests and linting are run using tox. Tox can be installed using pip (`pip install tox`). Run
the following command within the base repository directory:

```shell
tox
```

