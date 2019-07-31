import operator

import numpy as np
import pytest

import pandas as pd
import pandas.util.testing as tm


def test_none_to_nan():
    a = pd.arrays.StringArray._from_sequence(["a", None, "b"])
    assert a[1] is not None
    assert np.isnan(a[1])


def test_setitem_validates():
    a = pd.arrays.StringArray._from_sequence(["a", "b"])
    with pytest.raises(ValueError, match="10"):
        a[0] = 10

    with pytest.raises(ValueError, match="strings"):
        a[:] = np.array([1, 2])


@pytest.mark.parametrize(
    "input, method",
    [
        (["a", "b", "c"], operator.methodcaller("capitalize")),
        (["a", "b", "c"], operator.methodcaller("capitalize")),
        (["a b", "a bc. de"], operator.methodcaller("capitalize")),
    ],
)
def test_string_methods(input, method):
    a = pd.Series(input, dtype="string")
    b = pd.Series(input, dtype="object")
    result = method(a.str)
    expected = method(b.str)

    assert result.dtype.name == "string"
    tm.assert_series_equal(result.astype(object), expected)


def test_add():
    a = pd.Series(["a", "b", "c", None, None], dtype="string")
    b = pd.Series(["x", "y", None, "z", None], dtype="string")

    result = a + b
    expected = pd.Series(["ax", "by", None, None, None], dtype="string")
    tm.assert_series_equal(result, expected)

    result = a.add(b)
    tm.assert_series_equal(result, expected)

    result = a.radd(b)
    expected = pd.Series(["xa", "yb", None, None, None], dtype="string")
    tm.assert_series_equal(result, expected)

    result = a.add(b, fill_value="-")
    expected = pd.Series(["ax", "by", "c-", "-z", None], dtype="string")
    tm.assert_series_equal(result, expected)
