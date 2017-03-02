#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: GAN.py
# Author: Yuxin Wu <ppwwyyxxc@gmail.com>

import tensorflow as tf
import numpy as np
from tensorpack import (FeedfreeTrainer, TowerContext,
        get_global_step_var, QueueInput)
from tensorpack.tfutils.summary import summary_moving_average, add_moving_summary
from tensorpack.dataflow import DataFlow

class GANTrainer(FeedfreeTrainer):
    def __init__(self, config, g_vs_d=1):
        self._input_method = QueueInput(config.dataset)
        super(GANTrainer, self).__init__(config)
        if g_vs_d > 1:
            self._opt_g = g_vs_d
            self._opt_d = 1
        else:
            self._opt_g = 1
            self._opt_d = int(1.0 / g_vs_d)

    def _setup(self):
        super(GANTrainer, self)._setup()
        with TowerContext(''):
            actual_inputs = self._get_input_tensors()
            self.model.build_graph(actual_inputs)
        self.g_min = self.config.optimizer.minimize(self.model.g_loss,
                var_list=self.model.g_vars, name='g_op')
        self.d_min = self.config.optimizer.minimize(self.model.d_loss,
                var_list=self.model.d_vars, name='d_op')
        self.gs_incr = tf.assign_add(get_global_step_var(), 1, name='global_step_incr')
        self.summary_op = summary_moving_average()
        self.d_min = tf.group(self.d_min, self.summary_op)

    def run_step(self):
        for _ in range(self._opt_g):
            self.sess.run(self.g_min)
        for _ in range(self._opt_d):
            self.sess.run(self.d_min)
        self.sess.run(self.gs_incr)

class RandomZData(DataFlow):
    def __init__(self, shape):
        super(RandomZData, self).__init__()
        self.shape = shape
    def get_data(self):
        while True:
            yield [np.random.uniform(-1, 1, size=self.shape)]

def build_GAN_losses(vecpos, vecneg):
    sigmpos = tf.sigmoid(vecpos)
    sigmneg = tf.sigmoid(vecneg)
    tf.histogram_summary('sigmoid-pos', sigmpos)
    tf.histogram_summary('sigmoid-neg', sigmneg)

    d_loss_pos = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
        vecpos, tf.ones_like(vecpos)), name='d_CE_loss_pos')
    d_loss_neg = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
        vecneg, tf.zeros_like(vecneg)), name='d_CE_loss_neg')

    d_pos_acc = tf.reduce_mean(tf.cast(sigmpos > 0.5, tf.float32), name='pos_acc')
    d_neg_acc = tf.reduce_mean(tf.cast(sigmneg < 0.5, tf.float32), name='neg_acc')

    g_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(
        vecneg, tf.ones_like(vecneg)), name='g_CE_loss')
    d_loss = tf.add(d_loss_pos, d_loss_neg, name='d_CE_loss')
    add_moving_summary(d_loss_pos, d_loss_neg,
            g_loss, d_loss,
            d_pos_acc, d_neg_acc)
    return g_loss, d_loss
