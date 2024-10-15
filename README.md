# Datasentics Task

Andrea Chimenti  
October 2024

## Notes

### Version of Libraries

- The script should come with the `requirements.txt` file in order to specify the required version of libraries. E.g. `error_bad_lines` is not supported in new versions of pandas.
- The version of tools used should be agreed upon with the team.

### Approach

- `df.apply()` is the slowest option because under the hood it's just a for loop.
- `dataset_lowercase["Book-Title"] == "the fellowship of the ring (the lord of the rings, part 1)"` is probably too strict.
- Using `to_numpy()` in `tolkien_readers = tolkien_readers.tolist()` would be a better more consistent approach that could increase performance. In this case it would be probably negligible, but using numpy arrays and operations is generally faster.
- In new pandas versions it is better to use the `StyringDType` column type. See [doc](https://pandas.pydata.org/docs/user_guide/text.html).
- `groupby` should use the ISBN attribute which has primary key properties. **CAREFUL:** some books with the same name have different ISBNs.
- Making a shallow copy will modify the original dataframe.
- Old commented code??
- Naming consistency and readibility.
- The format of the csv should be inspected in order to successfully load all data. (quoting, delimiter, escape char etc.)
- Encoding?
- Think about using the implicit scores (could be used as a metric of user interest).

### Algorithm

- Does not take into account the rating that users gave to LOTR books.


### Improvements

- Dask dataframes?