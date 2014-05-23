#! /usr/bin/env python

# ----------------------------------------------------------------------------
# Copyright (c) 2013--, scikit-bio development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function
from future.utils.six import StringIO
from unittest import TestCase, main

import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from skbio.core.distance import DistanceMatrix
from skbio.math.stats.distance.bioenv import bioenv
from skbio.util.testing import get_data_path


class BIOENVTests(TestCase):
    """All results were verified with R (vegan::bioenv)."""

    def setUp(self):
        # TODO add description of test dataset
        self.dm_88_soils = DistanceMatrix.from_file(
            get_data_path('88_soils_dm.txt'))
        self.dm_88_soils_reordered = DistanceMatrix.from_file(
            get_data_path('88_soils_dm_reordered.txt'))

        self.df_88_soils = pd.read_csv(get_data_path('88_soils_df.txt'),
                                       sep='\t', index_col=0)
        self.df_88_soils_extra_column = pd.read_csv(
            get_data_path('88_soils_df_extra_column.txt'), sep='\t',
            index_col=0)
        self.cols = ['TOT_ORG_CARB', 'SILT_CLAY', 'ELEVATION',
                     'SOIL_MOISTURE_DEFICIT', 'CARB_NITRO_RATIO',
                     'ANNUAL_SEASON_TEMP', 'ANNUAL_SEASON_PRECPT', 'PH',
                     'CMIN_RATE', 'LONGITUDE', 'LATITUDE']

        self.exp_88_soils = pd.read_csv(
            get_data_path('88_soils_exp_results.txt'), sep='\t', index_col=0)
        self.exp_88_soils_single_column = pd.read_csv(
            get_data_path('88_soils_single_column_exp_results.txt'), sep='\t',
            index_col=0)
        self.exp_88_soils_different_column_order = pd.read_csv(
            get_data_path('88_soils_different_column_order_exp_results.txt'),
            sep='\t', index_col=0)

    def test_bioenv_all_columns_implicit(self):
        # Test with all columns in data frame (implicitly).
        obs = bioenv(self.dm_88_soils, self.df_88_soils)
        assert_frame_equal(obs, self.exp_88_soils)

        # Should get the same results if order of rows/cols in distance matrix
        # is changed.
        obs = bioenv(self.dm_88_soils_reordered, self.df_88_soils)
        assert_frame_equal(obs, self.exp_88_soils)

    def test_bioenv_all_columns_explicit(self):
        # Test with all columns being specified.
        obs = bioenv(self.dm_88_soils, self.df_88_soils, columns=self.cols)
        assert_frame_equal(obs, self.exp_88_soils)

        # Test against a data frame that has an extra non-numeric column and
        # some of the rows and columns reordered (we should get the same
        # result since we're specifying the same columns in the same order).
        obs = bioenv(self.dm_88_soils, self.df_88_soils_extra_column,
                     columns=self.cols)
        assert_frame_equal(obs, self.exp_88_soils)

    def test_bioenv_single_column(self):
        obs = bioenv(self.dm_88_soils, self.df_88_soils, columns=['PH'])
        assert_frame_equal(obs, self.exp_88_soils_single_column)

    def test_bioenv_different_column_order(self):
        # Specifying columns in a different order will change the row labels in
        # the results data frame as the column subsets will be reordered, but
        # the actual results shouldn't change unless there happens to be a tie
        # in the correlation coefficients at a particular subset size and a
        # different optimal subset is chosen (there isn't a tie in this
        # dataset).
        obs = bioenv(self.dm_88_soils, self.df_88_soils,
                     columns=self.cols[::-1])
        assert_frame_equal(obs, self.exp_88_soils_different_column_order)

    def test_bioenv_no_side_effects(self):
        # Deep copies of both primary inputs.
        dm_copy = self.dm_88_soils.copy()
        df_copy = self.df_88_soils.copy(deep=True)

        bioenv(self.dm_88_soils, self.df_88_soils)

        # Make sure we haven't modified the primary input in some way (e.g.,
        # with scaling, type conversions, etc.).
        self.assertEqual(self.dm_88_soils, dm_copy)
        assert_frame_equal(self.df_88_soils, df_copy)

    def test_bioenv_no_distance_matrix(self):
        with self.assertRaises(TypeError):
            bioenv('breh', self.df_88_soils)

    def test_bioenv_no_data_frame(self):
        with self.assertRaises(TypeError):
            bioenv(self.dm_88_soils, None)

    def test_bioenv_duplicate_columns(self):
        with self.assertRaises(ValueError):
            bioenv(self.dm_88_soils, self.df_88_soils,
                   columns=self.cols + ['PH'])

    def test_bioenv_no_columns(self):
        with self.assertRaises(ValueError):
            bioenv(self.dm_88_soils, self.df_88_soils, columns=[])

    def test_bioenv_missing_columns(self):
        with self.assertRaises(ValueError):
            bioenv(self.dm_88_soils, self.df_88_soils,
                   columns=self.cols + ['brofist'])

    def test_bioenv_missing_distance_matrix_ids(self):
        df = self.df_88_soils[1:]
        with self.assertRaises(ValueError):
            bioenv(self.dm_88_soils, df)

    def test_bioenv_nans(self):
        df = self.df_88_soils.replace(53.9, np.nan)
        with self.assertRaises(ValueError):
            bioenv(self.dm_88_soils, df)

    def test_bioenv_nonnumeric_columns(self):
        df = self.df_88_soils.replace(2400, 'no cog yay')
        with self.assertRaises(TypeError):
            bioenv(self.dm_88_soils, df)

        with self.assertRaises(TypeError):
            bioenv(self.dm_88_soils, self.df_88_soils_extra_column)


if __name__ == '__main__':
    main()
