"""The cache full block is responsible for storing the full block of data to disk."""
import sys
from dataclasses import dataclass

import dask.array as da

from epochalyst.pipeline.caching import store_raw
from epochalyst.pipeline.caching.dask_array.base_cache_block import BaseCacheBlock
from epochalyst.pipeline.caching.error import CachePipelineError

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self


@dataclass
class CacheColumnBlock(BaseCacheBlock):
    """The cache full block is responsible for storing the full block of data to disk.

    :param data_path: The path where the data will be stored.
    :param columns: The columns to store
    """

    column: int = -1

    def transform(self, X: da.Array) -> da.Array:
        """Save the data or load it if it already exists.

        :param X: The data to save
        """

        # Check if the data path is set
        if not self.data_path:
            raise CachePipelineError("data_path is required")

        # Check if data is already stored
        column = self._data_exists(X[:, self.column])

        # Return the data if it already exists
        if array is not None:
            concatenated_array = da.concatenate([X[:, :self.column], array[:, None]], axis=1).rechunk()
            return concatenated_array

        # Store the data
        da.to_npy_stack(self.data_path, X[:, self.column])

        # Create the new array
        concatenated_array = da.concatenate([X[:, : self.column], column[:, None]], axis=1)

        return X
