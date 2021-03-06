__author__ = 'Charlie'
import tensorflow as tf
import os, sys, inspect
import numpy as np
import tensorflow.examples.tutorials.mnist as mnist
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D

utils_folder = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "..")))
if utils_folder not in sys.path:
    sys.path.insert(0, utils_folder)
import TensorflowUtils as utils

FLAGS = tf.flags.FLAGS
tf.flags.DEFINE_integer("batch_size", "256", "Train batch size")
tf.flags.DEFINE_string("logs_dir", "logs/MNIST_logs/", "Path to logs dir")
tf.flags.DEFINE_float("regularization", "1e-4", "Regularization multiplier value")

IMAGE_SIZE = 28
MAX_ITERATIONS = 20001
LEARNING_RATE = 1e-3
NUM_LABELS = 10

COLORS = np.random.rand(NUM_LABELS)


def add_to_reg_loss_and_summary(W, b):
    tf.histogram_summary(W.name, W)
    tf.histogram_summary(b.name, b)
    tf.add_to_collection("losses", tf.nn.l2_loss(W))
    tf.add_to_collection("losses", tf.nn.l2_loss(b))


def inference_fc(image):
    with tf.name_scope("fc1") as scope:
        W_fc1 = utils.weight_variable([IMAGE_SIZE * IMAGE_SIZE, 50], name="W_fc1")
        b_fc1 = utils.bias_variable([50], name="b_fc1")
        add_to_reg_loss_and_summary(W_fc1, b_fc1)
        h_fc1 = tf.nn.tanh(tf.matmul(image, W_fc1) + b_fc1)

    with tf.name_scope("fc2") as scope:
        W_fc2 = utils.weight_variable([50, 50], name="W_fc2")
        b_fc2 = utils.bias_variable([50], name="b_fc2")
        add_to_reg_loss_and_summary(W_fc2, b_fc2)
        h_fc2 = tf.nn.tanh(tf.matmul(h_fc1, W_fc2) + b_fc2)

    with tf.name_scope("fc3") as scope:
        W_fc3 = utils.weight_variable([50, 3], name="W_fc3")
        b_fc3 = utils.bias_variable([3], name="b_fc3")
        add_to_reg_loss_and_summary(W_fc3, b_fc3)
        h_fc3 = tf.nn.tanh(tf.matmul(h_fc2, W_fc3) + b_fc3)

    with tf.name_scope("fc4") as scope:
        W_fc4 = utils.weight_variable([3, 50], name="W_fc4")
        b_fc4 = utils.bias_variable([50], name="b_fc4")
        add_to_reg_loss_and_summary(W_fc4, b_fc4)
        h_fc4 = tf.nn.tanh(tf.matmul(h_fc3, W_fc4) + b_fc4)

    with tf.name_scope("fc5") as scope:
        W_fc5 = utils.weight_variable([50, 50], name="W_fc5")
        b_fc5 = utils.bias_variable([50], name="b_fc5")
        add_to_reg_loss_and_summary(W_fc5, b_fc5)
        h_fc5 = tf.nn.tanh(tf.matmul(h_fc4, W_fc5) + b_fc5)
        # h_fc_dropout = tf.nn.dropout(h_fc5, 0.5)

    with tf.name_scope("fc6") as scope:
        W_fc6 = utils.weight_variable([50, IMAGE_SIZE * IMAGE_SIZE], name="W_fc6")
        b_fc6 = utils.bias_variable([IMAGE_SIZE * IMAGE_SIZE], name="b_fc6")
        add_to_reg_loss_and_summary(W_fc6, b_fc6)
        pred = tf.matmul(h_fc5, W_fc6) + b_fc6

    return h_fc3, pred


def inference_conv(image):
    # incomplete :/
    image_reshaped = tf.reshape(image, [-1, IMAGE_SIZE, IMAGE_SIZE, 1])
    with tf.name_scope("conv1") as scope:
        W_conv1 = utils.weight_variable([3, 3, 1, 32], name="W_conv1")
        b_conv1 = utils.bias_variable([32], name="b_conv1")
        add_to_reg_loss_and_summary(W_conv1, b_conv1)
        h_conv1 = tf.nn.tanh(utils.conv2d_basic(image_reshaped, W_conv1, b_conv1))

    with tf.name_scope("conv2") as scope:
        W_conv2 = utils.weight_variable([3, 3, 32, 64], name="W_conv2")
        b_conv2 = utils.bias_variable([64], name="b_conv2")
        add_to_reg_loss_and_summary(W_conv2, b_conv2)
        h_conv2 = tf.nn.tanh(utils.conv2d_strided(h_conv1, W_conv2, b_conv2))

    with tf.name_scope("conv3") as scope:
        W_conv3 = utils.weight_variable([3, 3, 64, 128], name="W_conv3")
        b_conv3 = utils.bias_variable([128], name="b_conv3")
        add_to_reg_loss_and_summary(W_conv3, b_conv3)
        h_conv3 = tf.nn.tanh(utils.conv2d_strided(h_conv2, W_conv3, b_conv3))

    with tf.name_scope("conv4") as scope:
        W_conv4 = utils.weight_variable([3, 3, 128, 256], name="W_conv4")
        b_conv4 = utils.bias_variable([256], name="b_conv4")
        add_to_reg_loss_and_summary(W_conv4, b_conv4)
        h_conv4 = tf.nn.tanh(utils.conv2d_strided(h_conv3, W_conv4, b_conv4))

def main(argv=None):
    print "Reading MNIST data..."
    data = mnist.input_data.read_data_sets("MNIST_data", one_hot=True)
    images = tf.placeholder(tf.float32, [None, IMAGE_SIZE * IMAGE_SIZE])
    tf.image_summary("Input", tf.reshape(images, [-1, IMAGE_SIZE, IMAGE_SIZE, 1]), max_images=1)
    print "Setting up inference..."
    encoded, output_image = inference_fc(images)
    tf.image_summary("Output", tf.reshape(output_image, [-1, IMAGE_SIZE, IMAGE_SIZE, 1]), max_images=1)

    print "Loss setup..."
    loss1 = tf.nn.l2_loss(tf.sub(output_image, images)) / (IMAGE_SIZE * IMAGE_SIZE)
    loss2 = tf.add_n(tf.get_collection("losses"))
    loss = loss1 + FLAGS.regularization * loss2
    tf.scalar_summary("Loss", loss)
    tf.scalar_summary("Encoder_loss", loss1)
    tf.scalar_summary("Reg_loss", loss2)

    print "Setting up optimizer..."
    train_op = tf.train.AdamOptimizer(LEARNING_RATE).minimize(loss)

    print 'Setting up graph summary...'
    summary_op = tf.merge_all_summaries()

    # print "Creating matplot fig"
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    with tf.Session() as sess:
        summary_writer = tf.train.SummaryWriter(FLAGS.logs_dir, sess.graph_def)
        print "Creating saver..."
        saver = tf.train.Saver()
        sess.run(tf.initialize_all_variables())
        ckpt = tf.train.get_checkpoint_state(FLAGS.logs_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            print "Model restored..."

        for step in xrange(MAX_ITERATIONS):
            batch_image, batch_label = data.train.next_batch(FLAGS.batch_size)
            feed_dict = {images: batch_image}
            if step % 100 == 0:
                summary_str, loss_val = sess.run([summary_op, loss], feed_dict=feed_dict)
                print "Step %d Train loss %f" % (step, loss_val)
                summary_writer.add_summary(summary_str, global_step=step)

            if step % 1000 == 0:
                saver.save(sess, FLAGS.logs_dir + "model.ckpt", global_step=step)
                test_compression = sess.run(encoded, feed_dict={images: data.test.images})
                labels = np.argmax(data.test.labels, axis=1).reshape((-1, 1))
                write_file = os.path.join(FLAGS.logs_dir, "checkpoint%d.txt" % step)
                write_arr = np.hstack((test_compression, np.argmax(data.test.labels, axis=1).reshape((-1, 1))))
                np.savetxt(write_file, write_arr)
                # ax.clear()
                # ax.scatter(test_compression[:, 0], test_compression[:, 1], test_compression[:, 2], s=10,
                #            c=COLORS[labels], marker='o')
                # plt.show()
            sess.run(train_op, feed_dict=feed_dict)


if __name__ == "__main__":
    tf.app.run()
