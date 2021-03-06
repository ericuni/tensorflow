#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import logging
import numpy as np
import sklearn as sk
import sys
import tensorflow as tf
import udf
from mnist_data import *

logging.basicConfig(level = logging.DEBUG, format = '%(levelname)s %(asctime)s [%(filename)s][%(lineno)d][%(funcName)s] %(message)s')
log = logging.getLogger()

log.info('tensorflow version: {0}'.format(tf.__version__))

data = load_data()

# model definition
'''
Flattening the data throws away information about the 2D structure of the image. Isn't that bad?
Well, the best computer vision methods do exploit this structure, and we will in later tutorials.
But the simple method we will be using here, a softmax regression (dened below), won't.
'''
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

