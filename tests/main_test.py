import argparse

import pytest

from dataprofiler.main import str2bool


def test_str2bool_with_valid_values():
    str_true: str = "True"
    bool_true: bool = True

    str_false: str = "False"
    bool_false: bool = False
    assert bool_true == str2bool(str_true) and bool_false == str2bool(str_false)


def test_str2bool_with_invalid_true_values():
    str_true: str = "1"
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool(str_true)


def test_str2bool_with_invalid_false_values():
    str_false: str = "0"
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool(str_false)
