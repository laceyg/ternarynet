#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: loadcaffe.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

from collections import namedtuple, defaultdict
from abc import abstractmethod
import numpy as np
import copy
import os

from six.moves import zip

from .utils import change_env, get_dataset_path
from .fs import download
from . import logger

__all__ = ['load_caffe', 'get_caffe_pb']

CAFFE_PROTO_URL = "https://github.com/BVLC/caffe/raw/master/src/caffe/proto/caffe.proto"

class CaffeLayerProcessor(object):
    def __init__(self, net):
        self.net = net
        self.layer_names = net._layer_names
        self.param_dict = {}
        self.processors = {
            'Convolution': self.proc_conv,
            'InnerProduct': self.proc_fc,
            'BatchNorm': self.proc_bn,
            'Scale': self.proc_scale
        }

    def process(self):
        for idx, layer in enumerate(self.net.layers):
            param = layer.blobs
            name = self.layer_names[idx]
            if layer.type in self.processors:
                logger.info("Processing layer {} of type {}".format(
                    name, layer.type))
                dic = self.processors[layer.type](idx, name, param)
                self.param_dict.update(dic)
            elif len(layer.blobs) != 0:
                logger.warn(
                        "{} layer contains parameters but is not supported!".format(layer.type))
        return self.param_dict

    def proc_conv(self, idx, name, param):
        assert len(param) <= 2
        assert param[0].data.ndim == 4
        # caffe: ch_out, ch_in, h, w
        W = param[0].data.transpose(2,3,1,0)
        if len(param) == 1:
            return {name + '/W': W}
        else:
            return {name + '/W': W,
                    name + '/b': param[1].data}

    def proc_fc(self, idx, name, param):
        # TODO caffe has an 'transpose' option for fc/W
        assert len(param) == 2
        prev_layer_name = self.net.bottom_names[name][0]
        prev_layer_output = self.net.blobs[prev_layer_name].data
        if prev_layer_output.ndim == 4:
            logger.info("FC layer {} takes spatial data.".format(name))
            W = param[0].data
            # original: outx(CxHxW)
            W = W.reshape((-1,) + prev_layer_output.shape[1:]).transpose(2,3,1,0)
            # become: (HxWxC)xout
        else:
            W = param[0].data.transpose()
        return {name + '/W': W,
                name + '/b': param[1].data}

    def proc_bn(self, idx, name, param):
        assert param[2].data[0] == 1.0
        return {name +'/mean/EMA': param[0].data,
                name +'/variance/EMA': param[1].data }

    def proc_scale(self, idx, name, param):
        bottom_name = self.net.bottom_names[name][0]
        # find the bn layer before this scaling
        for i, layer in enumerate(self.net.layers):
            if layer.type == 'BatchNorm':
                name2 = self.layer_names[i]
                bottom_name2 = self.net.bottom_names[name2][0]
                if bottom_name2 == bottom_name:
                    # scaling and BN share the same bottom, should merge
                    logger.info("Merge {} and {} into one BatchNorm layer".format(
                        name, name2))
                    return {name2 + '/beta': param[1].data,
                            name2 + '/gamma': param[0].data }
        # assume this scaling layer is part of some BN
        logger.error("Could not find a BN layer corresponding to this Scale layer!")
        raise ValueError()


def load_caffe(model_desc, model_file):
    """
    :return: a dict of params
    """
    with change_env('GLOG_minloglevel', '2'):
        import caffe
        caffe.set_mode_cpu()
        net = caffe.Net(model_desc, model_file, caffe.TEST)
    param_dict = CaffeLayerProcessor(net).process()
    logger.info("Model loaded from caffe. Params: " + \
                " ".join(sorted(param_dict.keys())))
    return param_dict

def get_caffe_pb():
    dir = get_dataset_path('caffe')
    caffe_pb_file = os.path.join(dir, 'caffe_pb2.py')
    if not os.path.isfile(caffe_pb_file):
        proto_path = download(CAFFE_PROTO_URL, dir)
        assert os.path.isfile(os.path.join(dir, 'caffe.proto'))
        ret = os.system('cd {} && protoc caffe.proto --python_out .'.format(dir))
        assert ret == 0, \
                "Command `protoc caffe.proto --python_out .` failed!"
    import imp
    return imp.load_source('caffepb', caffe_pb_file)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('model')
    parser.add_argument('weights')
    parser.add_argument('output')
    args = parser.parse_args()
    ret = load_caffe(args.model, args.weights)

    import numpy as np
    np.save(args.output, ret)

