#!/usr/bin/env python

import numpy as np

from features.wav_iterator import batcher
from features.hdf5_iterator import Hdf5Iterator

class FeatureMixer:

    def __init__(self, iterators, mix_method='sum', shape=None, pos=None, seed=0 ):
        '''
        FeatureMixer: Mixes feature iterators together, yielding an
        iterator over both the original input iterators and the mixed
        output.

        Args:
            iterators (list): a list of hdf5 file names or a list of iterators
            mix_method (str): how to mix features together. 'sum' is the only
                supported method
            shape (tuple): dimension of slices to extract; if None, will yield
                the full size for each dataset in the HDF5 file
            pos (tuple or None): optionally, tuple of ints or None, the same
                length as shape. Where not None, slices will always be extracted
                from the given position on that dimension. If None, slices
                will be extracted from random positions in that dimension.

        Iterator yields:
            tuple (mix, *features), total length equal to length of iterators + 1,
                and mix is the sum of the input features
        '''
        if isinstance(iterators[0], str):
            self.iterator = []
            for h5file_name in iterators:
                self.iterators = Hdf5Iterator(h5file_name,shape=shape,pos=pos,seed=seed)
        else:
            self.iterators = iterators
        self.mix_method = mix_method

    def __next__(self):
        next_example = next(zip(*self.iterators))
        if self.mix_method == 'sum':
            mixed_example = np.sum(next_example, axis=0)
        else:
            raise ValueError("Invalid mix_method: '{}'".format(mix_method))

        return (mixed_example, *next_example)

    def __iter__(self):
        return self


if __name__ == "__main__":
    # Some tests and examples
    from features.hdf5_iterator import mock_hdf5
    mock_hdf5()
    h = Hdf5Iterator("._test.h5")
    d = FeatureMixer((h,))
    mix = next(d)

    # Check that b has the right number of features
    assert len(mix) == 2

    # Check that summing sums
    d = FeatureMixer((h,h), mix_method='sum')
    mix, h1, h2 = next(d)
    assert np.sum(h1+h2) == np.sum(mix)

    # Check that one example is different from the next
    assert np.sum(mix - next(d)[0]) != 0