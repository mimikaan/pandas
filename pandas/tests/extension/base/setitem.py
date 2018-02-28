import operator

import numpy as np
import pytest

import pandas as pd
import pandas.util.testing as tm
from .base import BaseExtensionTests


class BaseSetitemTests(BaseExtensionTests):
    def test_setitem_scalar_series(self, data):
        arr = pd.Series(data)
        arr[0] = data[1]
        assert arr[0] == data[1]

    def test_setitem_sequence(self, data):
        arr = pd.Series(data)
        original = data.copy()

        arr[[0, 1]] = [data[1], data[0]]
        assert arr[0] == original[1]
        assert arr[1] == original[0]

    @pytest.mark.parametrize('as_array', [True, False])
    def test_setitem_sequence_mismatched_length_raises(self, data, as_array):
        ser = pd.Series(data)
        value = [data[0]]
        if as_array:
            value = type(data)(value)

        xpr = 'cannot set using a {} indexer with a different length'
        with tm.assert_raises_regex(ValueError, xpr.format('list-like')):
            ser[[0, 1]] = value

        with tm.assert_raises_regex(ValueError, xpr.format('slice')):
            ser[slice(3)] = value

    def test_setitem_empty_indxer(self, data):
        ser = pd.Series(data)
        original = ser.copy()
        ser[[]] = []
        self.assert_series_equal(ser, original)

    def test_setitem_sequence_broadcasts(self, data):
        arr = pd.Series(data)

        arr[[0, 1]] = data[2]
        assert arr[0] == data[2]
        assert arr[1] == data[2]

    @pytest.mark.parametrize('setter', ['loc', 'iloc'])
    def test_set_scalar(self, data, setter):
        arr = pd.Series(data)
        setter = getattr(arr, setter)
        operator.setitem(setter, 0, data[1])
        assert arr[0] == data[1]

    def test_set_loc_scalar_mixed(self, data):
        df = pd.DataFrame({"A": np.arange(len(data)), "B": data})
        df.loc[0, 'B'] = data[1]
        assert df.loc[0, 'B'] == data[1]

    def test_set_loc_scalar_single(self, data):
        df = pd.DataFrame({"B": data})
        df.loc[10, 'B'] = data[1]
        assert df.loc[10, 'B'] == data[1]

    def test_set_loc_scalar_multiple_homogoneous(self, data):
        df = pd.DataFrame({"A": data, "B": data})
        df.loc[10, 'B'] = data[1]
        assert df.loc[10, 'B'] == data[1]

    def test_set_iloc_scalar_mixed(self, data):
        df = pd.DataFrame({"A": np.arange(len(data)), "B": data})
        df.iloc[0, 1] = data[1]
        assert df.loc[0, 'B'] == data[1]

    def test_set_iloc_scalar_single(self, data):
        df = pd.DataFrame({"B": data})
        df.iloc[10, 0] = data[1]
        assert df.loc[10, 'B'] == data[1]

    def test_set_iloc_scalar_multiple_homogoneous(self, data):
        df = pd.DataFrame({"A": data, "B": data})
        df.iloc[10, 1] = data[1]
        assert df.loc[10, 'B'] == data[1]

    @pytest.mark.parametrize('as_callable', [True, False])
    def test_set_mask_aligned(self, data, as_callable):
        ser = pd.Series(data)
        mask = np.zeros(len(data), dtype=bool)
        mask[:2] = True

        if as_callable:
            mask2 = lambda x: mask
        else:
            mask2 = mask

        ser[mask2] = data[5:7]
        assert ser[0] == data[5]
        assert ser[1] == data[6]

    def test_set_mask_broadcast(self, data):
        ser = pd.Series(data)
        mask = np.zeros(len(data), dtype=bool)
        mask[:2] = True

        ser[mask] = data[10]
        assert ser[0] == data[10]
        assert ser[1] == data[10]

    def test_setitem_expand_columns(self, data):
        df = pd.DataFrame({"A": data})
        result = df.copy()
        result['B'] = 1
        expected = pd.DataFrame({"A": data, "B": [1] * len(data)})
        self.assert_frame_equal(result, expected)

        result = df.copy()
        result.loc[:, 'B'] = 1
        self.assert_frame_equal(result, expected)

    def test_setitem_expand_with_extension(self, data):
        df = pd.DataFrame({"A": [1] * len(data)})
        result = df.copy()
        result['B'] = data
        expected = pd.DataFrame({"A": [1] * len(data), "B": data})
        self.assert_frame_equal(result, expected)

        result = df.copy()
        result.loc[:, 'B'] = data
        self.assert_frame_equal(result, expected)
