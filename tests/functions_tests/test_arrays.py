import unittest

import chainer
import chainer.functions as F
from chainer import testing
import numpy as np
import onnx

import onnx_chainer
from onnx_chainer.testing import input_generator
from onnx_chainer.testing import test_onnxruntime


@testing.parameterize(
    # cast
    # {'ops': 'cast', 'input_shape': (1, 5),
    #  'input_argname': 'x',
    #  'args': {'typ': np.float16}},
    {'ops': 'cast', 'input_shape': (1, 5),
     'input_argname': 'x',
     'args': {'typ': np.float64}},

    # depth2space
    {'ops': 'depth2space', 'input_shape': (1, 12, 6, 6),
     'input_argname': 'X',
     'args': {'r': 2}},

    # pad
    {'ops': 'pad', 'input_shape': (1, 2, 3, 4),
     'input_argname': 'x',
     'args': {'pad_width': ((0, 0), (0, 0), (2, 2), (2, 2)),
              'mode': 'constant'}},
    {'ops': 'pad', 'input_shape': (1, 2, 3, 4),
     'input_argname': 'x',
     'args': {'pad_width': ((0, 0), (0, 0), (2, 2), (2, 2)),
              'mode': 'reflect'}},
    {'ops': 'pad', 'input_shape': (1, 2, 3, 4),
     'input_argname': 'x',
     'args': {'pad_width': ((0, 0), (0, 0), (2, 2), (2, 2)),
              'mode': 'edge'}},

    # reshape
    {'ops': 'reshape', 'input_shape': (1, 6),
     'input_argname': 'x',
     'args': {'shape': (1, 2, 1, 3)}},
    {'ops': 'reshape', 'input_shape': (1, 6),
     'input_argname': 'x',
     'args': {'shape': (1, 2, 1, 3)}},

    # space2depth
    {'ops': 'space2depth', 'input_shape': (1, 12, 6, 6),
     'input_argname': 'X',
     'args': {'r': 2}},

    # split_axis
    {'ops': 'split_axis', 'input_shape': (1, 6),
     'input_argname': 'x',
     'args': {'indices_or_sections': 2,
              'axis': 1, 'force_tuple': True}},
    {'ops': 'split_axis', 'input_shape': (1, 6),
     'input_argname': 'x',
     'args': {'indices_or_sections': 2,
              'axis': 1, 'force_tuple': False}},

    # squeeze
    {'ops': 'squeeze', 'input_shape': (1, 3, 1, 2),
     'input_argname': 'x',
     'args': {'axis': None}},
    {'ops': 'squeeze', 'input_shape': (1, 3, 1, 2, 1),
     'input_argname': 'x',
     'args': {'axis': (2, 4)}},

    # tile
    {'ops': 'tile', 'input_shape': (1, 5),
     'input_argname': 'x',
     'args': {'reps': (1, 2)}},

    # transpose
    {'ops': 'transpose', 'input_shape': (1, 5),
     'input_argname': 'x',
     'args': {'axes': None}},

    # copy
    {'ops': 'copy', 'input_shape': (1, 5),
     'input_argname': 'x',
     'args': {'dst': -1}},

    # get_item
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': slice(0, 2)}},
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': (slice(1))}},
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': (slice(1, None))}},
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': 0}},
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': np.array(0)}},
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': (None, slice(0, 2))}},
    {'ops': 'get_item', 'input_shape': (2, 2, 3),
     'input_argname': 'x',
     'args': {'slices': (Ellipsis, slice(0, 2))}},
    # get_item, combine newaxis, slice, single index, ellipsis
    {'ops': 'get_item', 'input_shape': (2, 2, 3, 3, 3, 4),
     'input_argname': 'x',
     'args': {'slices': (0, None, Ellipsis, 0, None, slice(0, 2), None, 0)}},

    # expand_dims
    {'ops': 'expand_dims', 'input_shape': (3,),
     'input_argname': 'x', 'args': {'axis': 0}},
    {'ops': 'expand_dims', 'input_shape': (3,),
     'input_argname': 'x', 'args': {'axis': 1}},
    {'ops': 'expand_dims', 'input_shape': (3,),
     'input_argname': 'x', 'args': {'axis': -2}},
)
class TestArrayOperators(unittest.TestCase):

    def setUp(self):

        class Model(chainer.Chain):

            def __init__(self, ops, args, input_argname):
                super(Model, self).__init__()
                self.ops = getattr(F, ops)
                self.args = args
                self.input_argname = input_argname

            def __call__(self, x):
                self.args[self.input_argname] = x
                return self.ops(**self.args)

        self.model = Model(self.ops, self.args, self.input_argname)
        self.x = input_generator.increasing(*self.input_shape)
        self.fn = self.ops + '.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, self.x, self.fn, opset_version=opset_version)


@testing.parameterize(
    {'opset_version': 1},
    {'opset_version': 4}
)
class TestConcat(unittest.TestCase):

    def setUp(self):
        class Model(chainer.Chain):

            def __init__(self):
                super(Model, self).__init__()

            def __call__(self, x1, x2):
                return F.concat((x1, x2))

        self.model = Model()
        self.x1 = input_generator.increasing(2, 5)
        self.x2 = input_generator.increasing(2, 4)
        self.fn = 'Concat.onnx'

    def test_output(self):
        for opset_version in range(
                onnx_chainer.MINIMUM_OPSET_VERSION,
                onnx.defs.onnx_opset_version() + 1):
            test_onnxruntime.check_output(
                self.model, (self.x1, self.x2), self.fn,
                opset_version=opset_version)
