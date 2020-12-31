from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging
import pytest
import unittest

import numpy as np
import tensorflow as tf
import pandas as pd
from autorecsys.pipeline.mapper import (
    DenseFeatureMapper,
    SparseFeatureMapper

)
from autorecsys.searcher.core import hyperparameters as hp_module
from tensorflow.python.util import nest


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress warning for running TF with CPU

logger = logging.getLogger(__name__)


class TestMappers(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()  # change to pytest-provided temporary directory
        tmpdir.join("test_mapper.ini").write("# testdata")

    def setUp(self):
        super(TestMappers, self).setUp()
        self.input_shape = 13
        self.batch = 2
        self.embed_dim = 8
        self.inputs = [tf.random.uniform([self.batch, self.input_shape], dtype=tf.float32)]
        self.sparse_inputs = pd.DataFrame(np.random.rand(self.batch, self.input_shape))
        # create pandas by series

    def test_DenseFeatureMapper(self):
        """
        Test class DenseFeatureMapper in mapper.py
        """
        hp = hp_module.HyperParameters()
        p = {
            'num_of_fields': 10,
            'embedding_dim': 4}  # units, num_layer, use_batchnorm, dropout
        interactor = DenseFeatureMapper(**p)

        # test get_state()
        sol_get_state = {
            'name': 'dense_feature_mapper_1',
            'num_of_fields': 10,
            'embedding_dim': 4}

        assert interactor.get_state() == sol_get_state

        # test set_state()
        p = {
            'num_of_fields': self.input_shape,
            'embedding_dim': self.embed_dim}
        sol_set_state = {
            'name': 'dense_feature_mapper_1',
            'num_of_fields': self.input_shape,
            'embedding_dim': self.embed_dim}

        interactor.set_state(p)
        ans_set_state = interactor.get_state()
        assert ans_set_state == sol_set_state

        output = interactor.build(hp, self.inputs)  # Act

        assert len(nest.flatten(output)) == 1
        assert isinstance(self.inputs, list), "input needs to be a list"
        assert output.shape[0] == self.batch  # row
        assert output.shape[1] == self.input_shape  # input shape
        assert output.shape[2] == self.embed_dim  # embed_dim

    def test_SparseFeatureMapper(self):
        """
        Test class SparseFeatureMapper in mapper.py
        """
        # set up
        hp = hp_module.HyperParameters()
        p = {
            'num_of_fields': 10,
            'hash_size': [2, 4, 10],
            'embedding_dim': 4}  # units, num_layer, use_batchnorm, dropout
        interactor = SparseFeatureMapper(**p)

        # test get_state()
        sol_get_state = {
            'name': 'sparse_feature_mapper_1',
            'num_of_fields': 10,
            'hash_size': [2, 4, 10],
            'embedding_dim': 4}

        assert interactor.get_state() == sol_get_state

        # test set_state()
        hash_size = self.sparse_inputs.nunique().tolist()
        p = {
            'num_of_fields': self.input_shape,
            'hash_size': hash_size,
            'embedding_dim': self.embed_dim}
        sol_set_state = {
            'name': 'sparse_feature_mapper_1',
            'num_of_fields': self.input_shape,
            'hash_size': hash_size,
            'embedding_dim': self.embed_dim}

        interactor.set_state(p)
        ans_set_state = interactor.get_state()
        assert ans_set_state == sol_set_state

        # add + 1 (?)
        # hash_size = [x + 1 for x in hash_size]
        inputs = [tf.convert_to_tensor(self.sparse_inputs.values, dtype=tf.int32)]
        interactor = SparseFeatureMapper(**p)
        output = interactor.build(hp, inputs)  # Act

        assert len(nest.flatten(output)) == 1
        assert output.shape[0] == self.batch  # Row
        assert output.shape[1] == self.input_shape  # input shape
        assert output.shape[2] == self.embed_dim  # embed_dim
