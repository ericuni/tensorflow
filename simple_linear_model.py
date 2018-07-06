#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import logging
import numpy as np
import sklearn as sk
import sys
import tensorflow as tf
import udf

logging.basicConfig(level = logging.DEBUG, format = '%(levelname)s %(asctime)s [%(filename)s][%(lineno)d][%(funcName)s] %(message)s')
log = logging.getLogger()

log.info('tensorflow version: {0}'.format(tf.__version__))

# data set
from tensorflow.examples.tutorials.mnist import input_data
data = input_data.read_data_sets("data/MNIST/", one_hot = True)
## 每个label 是一个10 个元素的vector, eg: [0. 0. 0. 0. 0. 0. 0. 1. 0. 0.] 将 7 点亮了, 因此label 是 7

log.info('data set brief:')
log.info('train set: {0} {1}'.format(data.train.images.shape, data.train.labels.shape)) ## (55000, 784) (55000, 10)
log.info('test set: {0} {1}'.format(data.test.images.shape, data.test.labels.shape))
log.info('validation set: {0} {1}'.format(data.validation.images.shape, data.validation.labels.shape))

img_size = 28
img_size_flat = img_size * img_size
img_shape = (img_size, img_size)
num_classes = 10 ## 0 - 9 共10 个数字

## 为了方便之后的比较, 把hot vector 转换为一个数字
data.test.cls = np.array([np.argmax(label) for label in data.test.labels])
log.info(data.test.cls[0:5])
udf.plot_images('test set example', images = data.test.images[0:9], img_shape = img_shape, cls_true = data.test.cls[0:9])

# model definition
x = tf.placeholder(tf.float32, [None, img_size_flat]) ## num * 784, None means that the tensor may hold an arbitrary number of images
y_true = tf.placeholder(tf.float32, [None, num_classes]) ## num * 10
y_true_cls = tf.placeholder(tf.int64, [None]) ## num * 1

weights = tf.Variable(tf.zeros([img_size_flat, num_classes])) ## 784 * 10
bias = tf.Variable(tf.zeros([num_classes])) ## 10 * 1

logits = tf.matmul(x, weights) + bias
y_pred = tf.nn.softmax(logits)
y_pred_cls = tf.argmax(y_pred, axis = 1)

cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(logits = logits, labels = y_true) ## 对logits 取softmax, 然后和 y_true 计算cross entropy
cost = tf.reduce_mean(cross_entropy) ## 对所有实例的 cross entropy 求平均
optimizer = tf.train.GradientDescentOptimizer(learning_rate = 0.5).minimize(cost)

correct_prediction = tf.equal(y_pred_cls, y_true_cls)
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# model train
batch_size = 100
iterations = 200
session = tf.Session()
session.run(tf.global_variables_initializer())
feed_dict_test = {x: data.test.images, y_true_cls: data.test.cls}
for i in range(iterations):
	x_batch, y_batch = data.train.next_batch(batch_size)
	feed_dict_train = {x: x_batch, y_true: y_batch}
	session.run(optimizer, feed_dict = feed_dict_train)
	if i % 10 == 0 or i == iterations - 1:
		acc = session.run(accuracy, feed_dict = feed_dict_test)
		log.info('accuracy after {0} iterations: {1}'.format(i, acc))

# evaluation
cls_true = data.test.cls
cls_pred = session.run(y_pred_cls, feed_dict = feed_dict_test)
cm = sk.metrics.confusion_matrix(y_true = cls_true, y_pred = cls_pred)
log.info('Confusion matrix:\n {0}'.format(cm))
udf.plot_confusion_matrix('Confusion matrix', cm, num_classes)

## plot error imgs
correct, cls_pred = session.run([correct_prediction, y_pred_cls], feed_dict = feed_dict_test)
incorrect = (correct == False)
images = data.test.images[incorrect]
cls_pred = cls_pred[incorrect]
cls_true = data.test.cls[incorrect]
udf.plot_images('error example', images = images[0:9], img_shape = img_shape, cls_true = cls_true[0:9], cls_pred = cls_pred[0:9])

w = session.run(weights)
udf.plot_weights('Weights', w, img_shape)

session.close()
sys.exit(0)

