from setuptools import setup

setup(
    name='onnx-chainer',
    packages=[
        'onnx_chainer',
        'onnx_chainer.functions',
        'onnx_chainer.functions',
    ],
    version='1.0.0a1',
    description='ONNX support for Chainer',
    author='Shunta Saito',
    author_email='shunta@preferred.jp',
    url='https://github.com/mitmul/onnx-chainer',
    keywords='ONNX Chainer model converter deep learning',
    install_requires=[
        'chainer>=3.2.0',
        'onnx>=1.0.0'
    ],
    tests_require=[
        'chainer>=3.2.0',
        'onnx>=1.0.0',
        'numpy',
    ],
    license='MIT',
)
