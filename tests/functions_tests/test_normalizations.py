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
    {
        'name': 'local_response_normalization',
        'input_argname': 'x',
        'args': {'k': 1, 'n': 3, 'alpha': 1e-4, 'beta': 0.75},
        'opset_version': 1
    },
    {
        'name': 'normalize',
        'input_argname': 'x',
        'args': {'axis': 1},
        'opset_version': 1
    }
)
class TestNormalizations(unittest.TestCase):

    def setUp(self):

        class Model(chainer.Chain):

            def __init__(self, ops, args, input_argname):
                super(Model, self).__init__()
                self.ops = ops
                self.args = args
                self.input_argname = input_argname

            def __call__(self, x):
                self.args[self.input_argname] = x
                return self.ops(**self.args)

        ops = getattr(F, self.name)
        self.model = Model(ops, self.args, self.input_argname)
        self.x = input_generator.increasing(2, 5, 3, 3)
        self.fn = self.name + '.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)


@testing.parameterize(
    {'kwargs': {}},
    {'kwargs': {'use_beta': False}},
    {'kwargs': {'use_gamma': False}},
)
class TestBatchNormalization(unittest.TestCase):

    def setUp(self):

        class Model(chainer.Chain):

            def __init__(self, **kwargs):
                super(Model, self).__init__()
                with self.init_scope():
                    self.bn = L.BatchNormalization(5, **kwargs)

            def __call__(self, x):
                return self.bn(x)

        self.model = Model(**self.kwargs)
        self.x = input_generator.increasing(2, 5)
        self.fn = 'BatchNormalization.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)
