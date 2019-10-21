Funcgen
=======

A small module for generating sets of function signatures and
corresponding function objects.

* `Documentation <https://funcgen.readthedocs.io/en/latest/>`_
* `Source <https://github.com/ConradBailey/funcgen>`_
* `PyPi Package <https://pypi.org/project/funcgen/>`_

Installation
------------
``funcgen`` requires ``Python >= 3.6`` because it relies on modern type annotations.
::

   pip install funcgen

Example
-------

>>> import funcgen
>>>
>>> def wrapper(present):
...     log(f'Wrapped {present.__name__}')
...     return present
...
>>> def test_wrapper():
...     for funcs in funcgen.all_valid_functions():
...         assert all(wrapper(f) == f for f in funcs)
...
>>> test_wrapper()
