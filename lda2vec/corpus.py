from collections import defaultdict
import numpy as np


class Corpus():
    def __init__(self):
        """ The corpus helps with tasks involving integer representations of
        words. This object is used to filter, subsample, and convert loose
        word indices to compact word indices.

        'Loose' word arrays are word indices given by a tokenizer. The word
        index is not necessarily representative of word's frequency rank, and
        so loose arrays tend to have 'gaps' of unused indices, which can make
        models less memory efficient. As a result, this class helps convert
        a loose array to a 'compact' one where the most common words have low
        indices, and the most infrequent have high indices.

        Corpus maintains a count of how many of each word it has seen so
        that it can later selectively filter frequent or rare words. However,
        since word popularity rank could change with incoming data the word
        index count must be updated fully and `self.finalize()` must be called
        before any filtering and subsampling operations can happen.

        >>> corpus = Corpus()
        >>> words_raw = np.arange(25).reshape((5, 5))
        >>> corpus.update_word_count(words_raw)
        >>> corpus.finalize()
        >>> # words_pruned = corpus.filter_count(words_raw, min_count=20)
        >>> # words_sub = corpus.subsample_frequent(words_pruned, thresh=1e-5)
        >>> # word_compact = corpus.convert_to_compact(words_sub)
        >>> # word_loose = corpus.covnert_to_loose(word_compact)
        >>> # np.all(word_loose == words_sub)
        """
        self.counts_loose = defaultdict(int)
        self._finalized = False

    def update_word_count(self, loose_array):
        """ Update the corpus word counts given a loose array of word indices.
        Can be called multiple times, but once `finalize` is called the word
        counts cannot be updated.

        Arguments
        ---------
        loose_array : int array
            Array of word indices.

        >>> corpus = Corpus()
        >>> corpus.update_word_count(np.arange(10))
        >>> corpus.update_word_count(np.arange(8))
        >>> corpus.counts_loose[0]
        2
        >>> corpus.counts_loose[9]
        1
        """
        self._check_unfinalized()
        uniques, counts = np.unique(np.ravel(loose_array), return_counts=True)
        for k, v in zip(uniques, counts):
            self.counts_loose[k] += v

    def finalize(self):
        """ Call `finalize` once done updating word counts. This means the
        object will no longer accept new word count data, but the loose
        to compact index mapping can be computed. This frees the object to
        filter, subsample, and compactify incoming word arrays.

        >>> corpus = Corpus()

        We'll update the word counts, making sure that word index 2
        is the most common word index.
        >>> corpus.update_word_count(np.arange(1) + 2)
        >>> corpus.update_word_count(np.arange(3) + 2)
        >>> corpus.update_word_count(np.arange(10) + 2)
        >>> corpus.update_word_count(np.arange(8) + 2)
        >>> corpus.counts_loose[2]
        4

        The corpus has not been finalized yet, and so the compact mapping
        has not yet been computed.

        >>> corpus.counts_compact[0]
        Traceback (most recent call last):
            ...
        AttributeError: Corpus instance has no attribute 'counts_compact'
        >>> corpus.finalize()
        >>> corpus.counts_compact[0]
        4
        >>> corpus.loose_to_compact[2]
        0
        >>> corpus.loose_to_compact[3]
        2
        """
        carr = sorted(self.counts_loose.items(), key=lambda x: x[1],
                      reverse=True)
        keys = np.array(carr)[:, 0]
        cnts = np.array(carr)[:, 1]
        order = np.argsort(cnts)[::-1].astype('int32')
        loose_cnts = cnts[order]
        loose_keys = keys[order]
        compact_keys = np.arange(keys.shape[0]).astype('int32')
        loose_to_compact = {l: c for l, c in zip(loose_keys, compact_keys)}
        self.loose_to_compact = loose_to_compact
        self.counts_compact = {loose_to_compact[l]: c for l, c in
                               zip(loose_keys, loose_cnts)}
        self._finalized = True

    def _check_finalized(self):
        msg = "self.finalized() must be called before any other array ops"
        assert self._finalized, msg

    def _check_unfinalized(self):
        msg = "Cannot update word counts after self.finalized()"
        msg += "has been called"
        assert not self._finalized, msg

    def filter_count(self, arr, max_count=0, min_count=20000, pad=-1):
        """ Replace word indices below min_count with the pad index.

        Arguments
        ---------
        arr : int array
            Source array whose values will be replaced
        pad : int
            Rare word indices will be replaced with this index
        min_count : int
            Replace words less frequently occuring than this count. This
            defines the threshold for what words are very rare
        max_count : int
            Replace words occuring more frequently than this count. This
            defines the threshold for very frequent words
        """

        self._check_finalized()
        raise NotImplemented

    def subsample_frequent(self, arr, pad=-1, threshold=1e-5):
        """ Subsample the most frequent words. This aggressively
        drops word with frequencies higher than `threshold`.

        .. math :: p(w) = 1.0 - \sqrt{\frac{threshold}{f(w)}}

        .. [1] Distributed Representations of Words and Phrases and
               their Compositionality. Mikolov, Tomas and Sutskever, Ilya
               and Chen, Kai and Corrado, Greg S and Dean, Jeff
               Advances in Neural Information Processing Systems 26
        """
        self._check_finalized()
        raise NotImplemented

    def convert_to_compact(self, arr):
        self._check_finalized()
        raise NotImplemented

    def convert_to_loose(self, arr):
        self._check_finalized()
        raise NotImplemented


def fast_replace(data, keys, values, skip_checks=False):
    """ Do a search-and-replace in array `data`.

    Arguments
    ---------
    data : int array
        Array of integers
    keys : int array
        Array of keys inside of `data` to be replaced
    values : int array
        Array of values that replace the `keys` array
    skip_checks : bool, default=False
        Optionally skip sanity checking the input.
    """
    assert np.allclose(keys.shape, values.shape)
    if not skip_checks:
        assert data.max() <= keys.max()
    idx = np.digitize(data, keys, right=True)
    new_data = values[idx]
    return new_data
