.. _duplicates:

****************
Duplicate Labels
****************

:class:`Index` objects are not required to be unique; you can have duplicate row or column labels.


Duplicate Label Propagation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general, disallowing duplicates is "sticky". It's preserved through operations.
When multiple DataFrames are involved in an operation, duplictes are disallowed
if *any* of the inputs disallow duplicates.


.. ipython:: python
   :okexcept:

   df1 = pd.Series(0, index=['a', 'b'], allows_duplicate_labels=False)
