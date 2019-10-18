from functools import reduce
import inspect
from inspect import Parameter, Signature
from itertools import product, cycle
import operator
import random

import pytest

import funcgen


@pytest.fixture
def make_param_combos():
    def _make_param_combos(names, kind, annotations, defaults):
        return [None] + [Parameter(name, kind, annotation=annotation, default=default)
                         for name, annotation, default in product(names, annotations, defaults)]
    return _make_param_combos


#@pytest.fixture
#def make_random_param_tuple():
#    def _make_random_param_tuple(name_prefix):
#        name_count = random.randint(1, 3)
#        names = [f'{name_prefix}{i}' for i in range(name_count)]
#
#        default_population = {Parameter.empty, None, 1, -1, 0.0, -0.0, '', b'', True, False}
#        default_count = random.randint(1, len(default_population))
#        defaults = random.sample(default_population, default_count)
#
#        annotation_population = {Parameter.empty, None, int, float, str, bytes, bool}
#        annotation_count = random.randint(1, len(annotation_population))
#        annotations = random.sample(annotation_population, annotation_count)
#
#        return (names, defaults, annotations)
#    return _make_random_param_tuple


#@pytest.fixture
#def random_param_tuples(make_random_param_tuple):
#    param_count = random.randint(0, 3)
#    return [make_random_param_tuple(f'arg{i}') for i in range(param_count)]


def test_all_valid_parameters_null():
    for kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY):
        assert [[]] == list(funcgen.valid_parameters(kind, []))


def test_all_valid_parameters_bad_kind():
    for kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD, int, None):
        with pytest.raises(ValueError):
            funcgen.valid_parameters(kind, [])


def test_all_param_combinations_one():
    param_names = ['_', 'arg1']
    param_defaults = [None, Parameter.empty]
    param_annotations = [None, Parameter.empty]
    for param_name, param_default, param_annotation in product(param_names, param_defaults, param_annotations):
        param_tuples = [([param_name], [param_default], [param_annotation])]
        for kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]:
            combos = list(funcgen.valid_parameters(kind, param_tuples))
            param = Parameter(param_name, kind, default=param_default, annotation=param_annotation)
            assert combos == [[], [param]]


#def test_all_param_combinations_random(random_param_tuples):
#    for kind in [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY]:
#        combos = list(funcgen.valid_parameters(kind, random_param_tuples))


@pytest.fixture
def all_valid_signatures_list():
    return list(funcgen.all_valid_signatures())


@pytest.fixture
def all_valid_signatures_set(all_valid_signatures_list):
    return set(all_valid_signatures_list)


def test_all_valid_sigs_uniqueness(all_valid_signatures_set, all_valid_signatures_list):
    assert len(all_valid_signatures_set) == len(all_valid_signatures_list)


def test_all_valid_sigs_content(all_valid_signatures_set, make_param_combos):
    annotations = [None, Parameter.empty]
    defaults = [None, Parameter.empty]
    arg1_combos = make_param_combos(['arg1'], Parameter.POSITIONAL_OR_KEYWORD, annotations, defaults)
    arg2_combos = make_param_combos(['arg2'], Parameter.POSITIONAL_OR_KEYWORD, annotations, defaults)
    kwarg1_combos = make_param_combos(['kwarg1'], Parameter.KEYWORD_ONLY, annotations, defaults)
    kwarg2_combos = make_param_combos(['kwarg2'], Parameter.KEYWORD_ONLY, annotations, defaults)
    defaults = [Parameter.empty]
    args_combos = make_param_combos(['args'], Parameter.VAR_POSITIONAL, annotations, defaults)
    kwargs_combos = make_param_combos(['kwargs'], Parameter.VAR_KEYWORD, annotations, defaults)

    for params in product(arg1_combos, arg2_combos, args_combos,
                          kwarg1_combos, kwarg2_combos, kwargs_combos):
        params = filter(None, params)
        try:
            sig = Signature(params)
            sig_return = sig.replace(return_annotation=None)
        except ValueError: # invalid signature
            continue

        if (('arg2' in sig.parameters and not 'arg1' in sig.parameters) or
            ('kwarg2' in sig.parameters and not 'kwarg1' in sig.parameters)):
            assert sig not in all_valid_signatures_set
            assert sig_return not in all_valid_signatures_set
            continue

        assert sig in all_valid_signatures_set
        all_valid_signatures_set.remove(sig)
        assert sig_return in all_valid_signatures_set
        all_valid_signatures_set.remove(sig_return)

    assert len(all_valid_signatures_set) == 0


def test_valid_functions_null():
    results = list(funcgen.valid_functions([]))
    assert results == []


def test_all_valid_functions_types():
    for func, static_func_class, static_func_instance, method in funcgen.all_valid_functions():
        assert inspect.isfunction(func)
        assert inspect.isfunction(static_func_class)
        assert inspect.isfunction(static_func_instance)
        assert inspect.ismethod(method)


def test_valid_functions_equivalence():
    for signature in funcgen.all_valid_signatures():
        func_generator = funcgen.valid_functions([signature])
        for func_tuple in func_generator:
            for func in func_tuple:
                assert inspect.signature(func) == signature


#def test_valid_functions_body_returns():
#    body = lambda: 42
#    for functions in funcgen.valid_functions(funcgen.all_valid_signatures(), body):
#        for function in functions:
#            try:
#                function() == 42
#            except:
#                print(inspect.signature(function))
#                print(funcgen.main.signature2call(inspect.signature(function)))
#                raise
