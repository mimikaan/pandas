import pytest
import numpy as np

import pandas as pd
from pandas.core.sparse.api import SparseDtype


@pytest.mark.parametrize("dtype, fill_value", [
    ('int', 0),
    ('float', np.nan),
    ('bool', False),
    ('object', np.nan),
    ('datetime64[ns]', pd.NaT),
    ('timedelta64[ns]', pd.NaT),
])
def test_inferred_dtype(dtype, fill_value):
    sparse_dtype = SparseDtype(dtype)
    result = sparse_dtype.fill_value
    if pd.isna(fill_value):
        assert pd.isna(result) and type(result) == type(fill_value)
    else:
        assert result == fill_value


def test_from_sparse_dtype():
    dtype = SparseDtype('float', 0)
    result = SparseDtype(dtype)
    assert result.fill_value == 0


def test_from_sparse_dtype_fill_value():
    dtype = SparseDtype('int', 1)
    result = SparseDtype(dtype, fill_value=2)
    expected = SparseDtype('int', 2)
    assert result == expected


@pytest.mark.parametrize('dtype, fill_value', [
    ('int', None),
    ('float', None),
    ('bool', None),
    ('object', None),
    ('datetime64[ns]', None),
    ('timedelta64[ns]', None),
    ('int', np.nan),
    ('float', 0),
])
def test_equal(dtype, fill_value):
    a = SparseDtype(dtype, fill_value)
    b = SparseDtype(dtype, fill_value)
    assert a == b
    assert b == a


def test_nans_equal():
    a = SparseDtype(float, float('nan'))
    b = SparseDtype(float, np.nan)
    assert a == b
    assert b == a


@pytest.mark.parametrize('a, b', [
    (SparseDtype('float64'), SparseDtype('float32')),
    (SparseDtype('float64'), SparseDtype('float64', 0)),
    (SparseDtype('float64'), SparseDtype('datetime64[ns]', np.nan)),
    (SparseDtype(int, pd.NaT), SparseDtype(float, pd.NaT)),
    (SparseDtype('float64'), np.dtype('float64')),
])
def test_not_equal(a, b):
    assert a != b


def test_construct_from_string_raises():
    with pytest.raises(TypeError):
        SparseDtype.construct_from_string('not a dtype')


@pytest.mark.parametrize("dtype, expected", [
    (SparseDtype(int), True),
    (SparseDtype(float), True),
    (SparseDtype(bool), True),
    (SparseDtype(object), False),
    (SparseDtype(str), False),
])
def test_is_numeric(dtype, expected):
    assert dtype._is_numeric is expected


def test_str_uses_object():
    result = SparseDtype(str).subtype
    assert result == np.dtype('object')


@pytest.mark.parametrize("string, expected", [
    ('Sparse[float64]', SparseDtype(np.dtype('float64'))),
    ('Sparse[float32]', SparseDtype(np.dtype('float32'))),
    ('Sparse[int]', SparseDtype(np.dtype('int'))),
    ('Sparse[str]', SparseDtype(np.dtype('str'))),
    ('Sparse[datetime64[ns]]', SparseDtype(np.dtype('datetime64[ns]'))),
])
def test_construct_from_string(string, expected):
    result = SparseDtype.construct_from_string(string)
    assert result == expected