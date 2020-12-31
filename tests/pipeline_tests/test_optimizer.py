from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging
import pytest
import unittest
import tensorflow as tf
from autorecsys.pipeline.optimizer import (
    RatingPredictionOptimizer,
)
from autorecsys.searcher.core import hyperparameters as hp_module
from tensorflow.python.util import nest

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress warning for running TF with CPU

logger = logging.getLogger(__name__)


class TestOptimizers(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def initdir(self, tmpdir):
        tmpdir.chdir()  # change to pytest-provided temporary directory
        tmpdir.join("test_optimizer.ini").write("# testdata")

    def setUp(self):
        super(TestOptimizers, self).setUp()
        self.batch = 2
        self.emb = 4
        self.inputs = [tf.random.uniform([self.batch, self.emb], dtype=tf.float32)]

    def test_RatingPredictionOptimizer(self):
        """
        Test class RatingPredictionOptimizer in optimizer.py
        """
        hp = hp_module.HyperParameters()
        interactor = RatingPredictionOptimizer()
        output = interactor.build(hp, self.inputs)
        assert len(nest.flatten(output)) == 1
        assert output.shape == self.batch
