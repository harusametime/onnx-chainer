import chainer
from onnx_chainer import onnx_helper


def convert_Dropout(
        func, opset_version, input_names,
        num_outputs, parameters):
    if opset_version == 1:
        return onnx_helper.make_node(
            'Dropout', input_names, num_outputs,
            is_test=0 if chainer.config.train else 1,
            ratio=func.dropout_ratio,
            consumed_inputs=[1]
        ),
    elif opset_version == 6:
        return onnx_helper.make_node(
            'Dropout', input_names, num_outputs,
            is_test=0 if chainer.config.train else 1,
            ratio=func.dropout_ratio,
        ),
    elif opset_version == 7:
        return onnx_helper.make_node(
            'Dropout', input_names, num_outputs,
            ratio=func.dropout_ratio,
        ),
