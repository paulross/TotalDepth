Unit Tests
=========================

This describes how unit testing is done in TotalDepth.


TotalDepth uses the following test frameworks:


* `pytest <https://docs.pytest.org/en/latest/>`_ - This is a basic minimum.
* `pytest-cov <https://pypi.org/project/pytest-cov/>`_ - Pytest's wrapper around Ned Batchelor's *excellent* coverage tool.
* `pytest-benchmark <https://pypi.org/project/pytest-benchmark/>`_ - For micro benchmarks.
* `Airspeed Velocity <https://github.com/airspeed-velocity/asv>`_ - For timeline benchmarks.


Basic Testing
--------------------

Simply::

    $ pytest tests/

This should take only a few tens of seconds. If you include the slow tests with ``--runslow`` this will take many minutes.

Testing With Test Coverage
-----------------------------

For complete coverage you need to run the slow tests and with the following command::

    $ pytest --cov=TotalDepth --cov-report html --runslow tests
