import unittest

import chainer
from chainer import testing
import onnx

import onnx_chainer
from onnx_chainer.testing import input_generator
from onnx_chainer.testing import test_onnxruntime


@testing.parameterize(
    {'info': 'Neg', 'ops': '-a'},
    {'info': 'Absolute', 'ops': 'abs(a)'},
    {'info': 'Clip', 'ops': 'chainer.functions.clip(a, 0.1, 0.2)'},
    {'info': 'Exp', 'ops': 'chainer.functions.exp(a)'},
    {'info': 'Sqrt', 'ops': 'chainer.functions.sqrt(a)'},
    {'info': 'PowVarConst',
     'ops': 'chainer.functions.math.basic_math.pow(a, 2)'},
    {'info': 'Sum', 'ops': 'chainer.functions.sum(a)'},
    {'info': 'Sum', 'ops': 'chainer.functions.sum(a, axis=1)'},
    {'info': 'Sum', 'ops': 'chainer.functions.sum(a, keepdims=True)'},
    {'info': 'AddConstant', 'ops': 'a + 1'},
    {'info': 'Max', 'ops': 'chainer.functions.max(a)'},
    {'info': 'Max', 'ops': 'chainer.functions.max(a, axis=0)'},
    {'info': 'Max', 'ops': 'chainer.functions.max(a, keepdims=True)'},
    {'info': 'Mean', 'ops': 'chainer.functions.mean(a)'},
    {'info': 'Mean', 'ops': 'chainer.functions.mean(a, axis=0)'},
    {'info': 'Mean', 'ops': 'chainer.functions.mean(a, keepdims=True)'},
    {'info': 'Min', 'ops': 'chainer.functions.min(a)'},
    {'info': 'Min', 'ops': 'chainer.functions.min(a, axis=0)'},
    {'info': 'Min', 'ops': 'chainer.functions.min(a, keepdims=True)'},
    {'info': 'Prod', 'ops': 'chainer.functions.prod(a)'},
    {'info': 'Prod', 'ops': 'chainer.functions.prod(a, axis=0)'},
    {'info': 'Prod', 'ops': 'chainer.functions.prod(a, keepdims=True)'},
    {'info': 'LogSumExp', 'ops': 'chainer.functions.logsumexp(a)'},
    {'info': 'LogSumExp', 'ops': 'chainer.functions.logsumexp(a, axis=0)'},
    {'info': 'Square', 'ops': 'chainer.functions.square(a)'},
    {'info': 'BroadcastTo',
     'ops': 'chainer.functions.broadcast_to(a, (2,2,3))'},
)
class TestUnaryMathOperators(unittest.TestCase):

    def setUp(self):
        class Model(chainer.Chain):

            def __init__(self, ops):
                super(Model, self).__init__()
                self.ops = ops

            def __call__(self, a):
                if not isinstance(a, chainer.Variable):
                    a = chainer.Variable(a)
                return eval(self.ops)

        self.model = Model(self.ops)
        self.a = chainer.Variable(input_generator.positive_increasing(2, 3))
        self.fn = self.info + '.onnx'

    def test_output(self):
        opset_ids = onnx_chainer.mapping.operators[self.info]
        minimum_version = max(onnx_chainer.MINIMUM_OPSET_VERSION, opset_ids[0])

        for opset_version in range(
                minimum_version,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.a, self.fn, opset_version=opset_version)


@testing.parameterize(
    {'info': 'Add', 'ops': 'a + b'},
    {'info': 'Sub', 'ops': 'a - b'},
    {'info': 'Mul', 'ops': 'a * b'},
    {'info': 'Div', 'ops': 'a / b'},
    {'info': 'MatMul', 'ops': 'chainer.functions.matmul(a, b, transb=True)'},
    {'info': 'Maximum', 'ops': 'chainer.functions.maximum(a, b)'},
    {'info': 'Minimum', 'ops': 'chainer.functions.minimum(a, b)'},
)
class TestBinaryMathOperators(unittest.TestCase):

    def setUp(self):
        class Model(chainer.Chain):

            def __init__(self, ops):
                super(Model, self).__init__()
                self.ops = ops

            def __call__(self, a, b):
                if not isinstance(a, chainer.Variable):
                    a = chainer.Variable(a)
                if not isinstance(b, chainer.Variable):
                    b = chainer.Variable(b)
                return eval(self.ops)

        self.model = Model(self.ops)
        a = chainer.Variable(input_generator.increasing(2, 3))
        b = chainer.Variable(input_generator.nonzero_increasing(2, 3) * 0.3)
        self.x = (a, b)
        self.fn = self.info + '.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)


@testing.parameterize(
    {'info': 'LinearInterpolate',
     'ops': 'chainer.functions.linear_interpolate(a, b, c)'},
)
class TestTernaryMathOperators(unittest.TestCase):

    def setUp(self):
        class Model(chainer.Chain):

            def __init__(self, ops):
                super(Model, self).__init__()
                self.ops = ops

            def __call__(self, a, b, c):
                if not isinstance(a, chainer.Variable):
                    a = chainer.Variable(a)
                if not isinstance(b, chainer.Variable):
                    b = chainer.Variable(b)
                if not isinstance(c, chainer.Variable):
                    c = chainer.Variable(c)
                return eval(self.ops)

        self.model = Model(self.ops)
        a = chainer.Variable(input_generator.increasing(2, 3))
        b = chainer.Variable(input_generator.increasing(2, 3) * 0.3)
        c = chainer.Variable(input_generator.increasing(2, 3) * 0.7)
        self.x = (a, b, c)
        self.fn = self.info + '.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)
