# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

import numpy as np
from scipy.spatial.distance import pdist, squareform

from skbio.stats.distance import DistanceMatrix
from skbio.util._decorator import experimental, deprecated


@experimental(as_of="0.4.0")
def pw_distances(counts, ids=None, metric="braycurtis"):
    """Compute distances between all pairs of columns in a counts matrix

    Parameters
    ----------
    counts : 2D array_like of ints or floats
        Matrix containing count/abundance data where each row contains counts
        of observations in a given sample.
    ids : iterable of strs, optional
        Identifiers for each sample in ``counts``.
    metric : str, optional
        The name of the pairwise distance function to use when generating
        pairwise distances. See the scipy ``pdist`` docs, linked under *See
        Also*, for available metrics.

    Returns
    -------
    skbio.DistanceMatrix
        Distances between all pairs of samples (i.e., rows). The number of
        row and columns will be equal to the number of rows in ``counts``.

    Raises
    ------
    ValueError
        If ``len(ids) != len(counts)``.

    See Also
    --------
    scipy.spatial.distance.pdist
    pw_distances_from_table

    """
    num_samples = len(counts)
    if ids is not None and num_samples != len(ids):
        raise ValueError(
            "Number of rows in counts must be equal to number of provided "
            "ids.")

    distances = pdist(counts, metric)
    return DistanceMatrix(
        squareform(distances, force='tomatrix', checks=False), ids)

pw_distances_from_table_deprecation_reason = (
    "In the future, pw_distance will take a biom.table.Table object "
    "and this function will be removed. You will need to update your "
    "code to call pw_distances at that time.")


@deprecated(as_of="0.4.0", until="0.4.1",
            reason=pw_distances_from_table_deprecation_reason)
def pw_distances_from_table(table, metric="braycurtis"):
    """Compute distances between all pairs of samples in table

    Parameters
    ----------
    table : biom.table.Table
        ``Table`` containing count/abundance data of observations across
        samples.
    metric : str, optional
        The name of the pairwise distance function to use when generating
        pairwise distances. See the scipy ``pdist`` docs, linked under *See
        Also*, for available metrics.

    Returns
    -------
    skbio.DistanceMatrix
        Distances between all pairs of samples. The number of row and columns
        will be equal to the number of samples in ``table``.

    See Also
    --------
    scipy.spatial.distance.pdist
    biom.table.Table
    pw_distances

    """
    sample_ids = table.ids(axis="sample")
    num_samples = len(sample_ids)

    # initialize the result object
    dm = np.zeros((num_samples, num_samples))
    for i, sid1 in enumerate(sample_ids):
        v1 = table.data(sid1)
        for j, sid2 in enumerate(sample_ids[:i]):
            v2 = table.data(sid2)
            dm[i, j] = dm[j, i] = pdist([v1, v2], metric)
    return DistanceMatrix(dm, sample_ids)
