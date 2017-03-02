# Trained Ternary Quantization (TTQ)

This repo is a fork of the [Trained Ternary Quantization](https://arxiv.org/pdf/1612.01064v1) (Zhu et al.) [TensorFlow implementation](https://github.com/czhu95/ternarynet), which is used as a demonstration for training large deep learning models on the SHARCNET copper cluster.

This implementation is based on the [tensorpack](https://github.com/ppwwyyxx/tensorpack) neural network toolbox.  We add tensorpack as a `git subtree` that can be updated independent of the main project.  Please note that this code is based on an old revision of tensorpack (December 6, 2016):

```
git subtree add --prefix tools/tensorpack/ https://github.com/ppwwyyxx/tensorpack.git 1f02847da50ff1214e692e42061977196b25b2b1
```

## Copper Installation:

+ Sign up for [Compute Canada](https://www.computecanada.ca/) account
+ Login to copper:
```
ssh copper.sharcnet.ca
```
+ Build precompiled [TensorFlow v0.9 with CUDA 7.5 and cuDNN v4](https://www.sharcnet.ca/help/index.php/Tensorflow#Testing_Tensorflow_0.9_with_CUDA7.5_.2B_cuDNNv4_on_Copper)
+ Install tensorpack requirements:
```
pip install --user -r requirements.txt
pip install --user -r opt-requirements.txt
```
+ Clone this repo and setup copper environment:
```
git clone https://github.com/laceyg/ternarynet
cd ternarynet
source scripts/setup_COP.sh
```

## Dependencies:

+ Python 2 or 3
+ TensorFlow >= 0.8
+ Python bindings for OpenCV
+ Tensorpack [requirements](https://github.com/ppwwyyxx/tensorpack/blob/master/requirements.txt)


## Usage

+ To train AlexNet on ImageNet inside interactive job:
```
cd examples/Ternary-Net/
python ./tw-imagenet-alexnet.py --gpu 0,1,2,3 --data /tmp/MLRG/ilsvrc12 [--t threshold]
```
**Note: We used 4 GPUs for training**

## Experimental Results:

#### Error Rate of TTQ AlexNet model on ImageNet from scratch:

| Network       | Full Precision | TTQ         |
| ------------- | ------------- | ----------- |
| Top1-error    | 42.8          | 42.5        |
| Top5-error    | 19.7          | 20.3        |
