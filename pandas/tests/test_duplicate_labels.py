"""Tests dealing with the NDFrame.allows_duplicates."""
import operator

import pytest

import pandas.errors

import pandas as pd

# ----------------------------------------------------------------------------
# Preservation


@pytest.mark.parametrize(
    "cls, data",
    [
        (pd.Series, []),
        (pd.Series, [1, 2]),
        (pd.DataFrame, {}),
        (pd.DataFrame, {"A": [1, 2]}),
    ],
)
def test_construction_ok(cls, data):
    result = cls(data)
    assert result.allows_duplicate_labels is True

    result = cls(data, allow_duplicate_labels=False)
    assert result.allows_duplicate_labels is False


@pytest.mark.parametrize(
    "func",
    [
        operator.itemgetter(["a"]),
        operator.methodcaller("add", 1),
        operator.methodcaller("rename", str.upper),
        operator.methodcaller("rename", "name"),
        operator.methodcaller("abs"),
        # TODO: test np.abs
    ],
)
def test_preserved_series(func):
    s = pd.Series([0, 1], index=["a", "b"], allow_duplicate_labels=False)
    assert func(s).allows_duplicate_labels is False


@pytest.mark.parametrize(
    "other", [pd.Series(0, index=["a", "b", "c"]), pd.Series(0, index=["a", "b"])]
)
# TODO: frame
def test_align(other):
    s = pd.Series([0, 1], index=["a", "b"], allow_duplicate_labels=False)
    a, b = s.align(other)
    assert a.allows_duplicate_labels is False
    assert b.allows_duplicate_labels is False


def test_preserved_frame():
    df = pd.DataFrame(
        {"A": [1, 2], "B": [3, 4]}, index=["a", "b"], allow_duplicate_labels=False
    )
    assert df.loc[["a"]].allows_duplicate_labels is False
    assert df.loc[:, ["A", "B"]].allows_duplicate_labels is False


def test_to_frame():
    s = pd.Series(allow_duplicate_labels=False)
    assert s.to_frame().allows_duplicate_labels is False


@pytest.mark.parametrize("func", ["add", "sub"])
@pytest.mark.parametrize("frame", [False, True])
@pytest.mark.parametrize("other", [1, pd.Series([1, 2], name="A")])
def test_binops(func, other, frame):
    df = pd.Series([1, 2], name="A", index=["a", "b"], allow_duplicate_labels=False)
    if frame:
        df = df.to_frame()
    if isinstance(other, pd.Series) and frame:
        other = other.to_frame()
    func = operator.methodcaller(func, other)
    assert df.allows_duplicate_labels is False
    assert func(df).allows_duplicate_labels is False


@pytest.mark.xfail(reason="TODO")
def test_preserve_getitem():
    df = pd.DataFrame({"A": [1, 2]}, allow_duplicate_labels=False)
    assert df[["A"]].allows_duplicate_labels is False
    assert df["A"].allows_duplicate_labels is False
    assert df.loc[0].allows_duplicate_labels is False
    assert df.loc[[0]].allows_duplicate_labels is False
    assert df.loc[0, ["A"]].allows_duplicate_labels is False


@pytest.mark.parametrize(
    "objs, kwargs",
    [
        # Series
        (
            [
                pd.Series(1, index=["a", "b"], allow_duplicate_labels=False),
                pd.Series(2, index=["c", "d"], allow_duplicate_labels=False),
            ],
            {},
        ),
        (
            [
                pd.Series(1, index=["a", "b"], allow_duplicate_labels=False),
                pd.Series(2, index=["a", "b"], allow_duplicate_labels=False),
            ],
            {"ignore_index": True},
        ),
        (
            [
                pd.Series(1, index=["a", "b"], allow_duplicate_labels=False),
                pd.Series(2, index=["a", "b"], allow_duplicate_labels=False),
            ],
            {"axis": 1},
        ),
        # Frame
        (
            [
                pd.DataFrame(
                    {"A": [1, 2]}, index=["a", "b"], allow_duplicate_labels=False
                ),
                pd.DataFrame(
                    {"A": [1, 2]}, index=["c", "d"], allow_duplicate_labels=False
                ),
            ],
            {},
        ),
        (
            [
                pd.DataFrame(
                    {"A": [1, 2]}, index=["a", "b"], allow_duplicate_labels=False
                ),
                pd.DataFrame(
                    {"A": [1, 2]}, index=["a", "b"], allow_duplicate_labels=False
                ),
            ],
            {"ignore_index": True},
        ),
        (
            [
                pd.DataFrame(
                    {"A": [1, 2]}, index=["a", "b"], allow_duplicate_labels=False
                ),
                pd.DataFrame(
                    {"B": [1, 2]}, index=["a", "b"], allow_duplicate_labels=False
                ),
            ],
            {"axis": 1},
        ),
        # Series / Frame
        (
            [
                pd.DataFrame(
                    {"A": [1, 2]}, index=["a", "b"], allow_duplicate_labels=False
                ),
                pd.Series(
                    [1, 2], index=["a", "b"], name="B", allow_duplicate_labels=False
                ),
            ],
            {"axis": 1},
        ),
    ],
)
def test_concat(objs, kwargs):
    result = pd.concat(objs, **kwargs)
    assert result.allows_duplicate_labels is False


@pytest.mark.parametrize(
    "left, right, kwargs, expected",
    [
        # false false false
        (
            pd.DataFrame({"A": [0, 1]}, index=["a", "b"], allow_duplicate_labels=False),
            pd.DataFrame({"B": [0, 1]}, index=["a", "d"], allow_duplicate_labels=False),
            dict(left_index=True, right_index=True),
            False,
        ),
        # false true false
        (
            pd.DataFrame({"A": [0, 1]}, index=["a", "b"], allow_duplicate_labels=False),
            pd.DataFrame({"B": [0, 1]}, index=["a", "d"]),
            dict(left_index=True, right_index=True),
            False,
        ),
        # true true true
        (
            pd.DataFrame({"A": [0, 1]}, index=["a", "b"]),
            pd.DataFrame({"B": [0, 1]}, index=["a", "d"]),
            dict(left_index=True, right_index=True),
            True,
        ),
    ],
)
def test_merge(left, right, kwargs, expected):
    result = pd.merge(left, right, **kwargs)
    assert result.allows_duplicate_labels is expected


# ----------------------------------------------------------------------------
# Raises


@pytest.mark.parametrize(
    "cls, axes",
    [
        (pd.Series, {"index": ["a", "a"]}),
        (pd.DataFrame, {"index": ["a", "a"]}),
        (pd.DataFrame, {"index": ["a", "a"], "columns": ["b", "b"]}),
        (pd.DataFrame, {"columns": ["b", "b"]}),
    ],
)
def test_construction_with_duplicates(cls, axes):
    result = cls(**axes)
    assert result._allows_duplicate_labels is True

    with pytest.raises(pandas.errors.DuplicateLabelError):
        cls(**axes, allow_duplicate_labels=False)


@pytest.mark.parametrize(
    "data",
    [pd.Series(index=[0, 0]), pd.DataFrame(index=[0, 0]), pd.DataFrame(columns=[0, 0])],
)
def test_setting_allows_duplicate_labels_raises(data):
    with pytest.raises(pandas.errors.DuplicateLabelError):
        data.allows_duplicate_labels = False

    assert data.allows_duplicate_labels is True


@pytest.mark.parametrize(
    "func", [operator.methodcaller("append", pd.Series(0, index=["a", "b"]))]
)
def test_series_raises(func):
    s = pd.Series([0, 1], index=["a", "b"], allow_duplicate_labels=False)
    with pytest.raises(pandas.errors.DuplicateLabelError):
        func(s)


@pytest.mark.parametrize(
    "getter, target",
    [
        (operator.itemgetter(["A", "A"]), None),
        # loc
        (operator.itemgetter(["a", "a"]), "loc"),
        pytest.param(
            operator.itemgetter(("a", ["A", "A"])),
            "loc",
            marks=pytest.mark.xfail(reason="TODO"),
        ),
        pytest.param(
            operator.itemgetter((["a", "a"], "A")),
            "loc",
            marks=pytest.mark.xfail(reason="TODO"),
        ),
        # iloc
        (operator.itemgetter([0, 0]), "iloc"),
        pytest.param(
            operator.itemgetter((0, [0, 0])),
            "iloc",
            marks=pytest.mark.xfail(reason="TODO"),
        ),
        pytest.param(
            operator.itemgetter(([0, 0], 0)),
            "iloc",
            marks=pytest.mark.xfail(reason="TODO"),
        ),
    ],
)
def test_getitem_raises(getter, target):
    df = pd.DataFrame(
        {"A": [1, 2], "B": [3, 4]}, index=["a", "b"], allow_duplicate_labels=False
    )
    if target:
        # df, df.loc, or df.iloc
        target = getattr(df, target)
    else:
        target = df

    with pytest.raises(pandas.errors.DuplicateLabelError):
        getter(target)


@pytest.mark.parametrize(
    "objs, kwargs",
    [
        (
            [
                pd.Series(1, index=[0, 1], name="a", allow_duplicate_labels=False),
                pd.Series(2, index=[0, 1], name="a", allow_duplicate_labels=False),
            ],
            {"axis": 1},
        )
    ],
)
def test_concat_raises(objs, kwargs):
    with pytest.raises(pandas.errors.DuplicateLabelError):
        pd.concat(objs, **kwargs)


def test_merge_raises():
    a = pd.DataFrame(
        {"A": [0, 1, 2]}, index=["a", "b", "c"], allow_duplicate_labels=False
    )
    b = pd.DataFrame({"B": [0, 1, 2]}, index=["a", "b", "b"])
    with pytest.raises(pandas.errors.DuplicateLabelError):
        pd.merge(a, b, left_index=True, right_index=True)