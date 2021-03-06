import unittest

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import testing
import onnx

import onnx_chainer
from onnx_chainer.testing import input_generator
from onnx_chainer.testing import test_onnxruntime


@testing.parameterize(
    {'name': 'clipped_relu'},
    {'name': 'elu'},
    {'name': 'hard_sigmoid'},
    {'name': 'leaky_relu'},
    {'name': 'log_softmax'},
    {'name': 'relu'},
    {'name': 'sigmoid'},
    {'name': 'softmax'},
    {'name': 'softplus'},
    {'name': 'tanh'},
)
class TestActivations(unittest.TestCase):

    def setUp(self):

        class Model(chainer.Chain):

            def __init__(self, ops):
                super(Model, self).__init__()
                self.ops = ops

            def __call__(self, x):
                return self.ops(x)

        ops = getattr(F, self.name)
        self.model = Model(ops)
        self.x = input_generator.increasing(2, 5)
        self.fn = self.name + '.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)


class TestPReLU(unittest.TestCase):

    def setUp(self):

        class Model(chainer.Chain):

            def __init__(self):
                super(Model, self).__init__()
                with self.init_scope():
                    self.prelu = L.PReLU()

            def __call__(self, x):
                return self.prelu(x)

        self.model = Model()
        self.x = input_generator.increasing(2, 5)
        self.fn = 'PReLU.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)
