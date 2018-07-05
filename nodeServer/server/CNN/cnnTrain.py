import numpy as np
import tensorflow as tf

import os
import json

from dltk.core.metrics import dice
from dltk.networks.segmentation.unet import residual_unet_3d
from dltk.io.abstract_reader import Reader

from imageReader import readFunc

#from tensorflow.python.client import device_lib
#print(device_lib.list_local_devices())

def model_fn(features, labels, mode, params):
    """Model function to construct a tf.estimator.EstimatorSpec. It creates a
        network given input features (e.g. from a dltk.io.abstract_reader) and
        training targets (labels). Further, loss, optimiser, evaluation ops and
        custom tensorboard summary ops can be added. For additional information,
        please refer to https://www.tensorflow.org/api_docs/python/tf/estimator/Estimator#model_fn.

    Args:
        features (tf.Tensor): Tensor of input features to train from. Required
            rank and dimensions are determined by the subsequent ops
            (i.e. the network).
        labels (tf.Tensor): Tensor of training targets or labels. Required rank
            and dimensions are determined by the network output.
        mode (str): One of the tf.estimator.ModeKeys: TRAIN, EVAL or PREDICT
        params (dict, optional): A dictionary to parameterise the model_fn
            (e.g. learning_rate)

    Returns:
        tf.estimator.EstimatorSpec: A custom EstimatorSpec for this experiment
    """

    # 1. create a model and its outputs
    net_output_ops = residual_unet_3d(
        inputs=features['x'],
        num_classes=params["numClasses"],
        num_res_units=2,
        filters=(16, 32, 64, 128),
        strides=((1, 1, 1), (1, 2, 2), (1, 2, 2), (1, 2, 2)),
        mode=mode,
        kernel_regularizer=tf.contrib.layers.l2_regularizer(1e-4))

    # 1.1 Generate predictions only (for `ModeKeys.PREDICT`)
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(
            mode=mode,
            predictions=net_output_ops,
            export_outputs={'out': tf.estimator.export.PredictOutput(net_output_ops)})

    # 2. set up a loss function
    ce = tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits=net_output_ops['logits'],
        labels=labels['y'])
    loss = tf.reduce_mean(ce)

    # 3. define a training op and ops for updating moving averages
    # (i.e. for batch normalisation)
    global_step = tf.train.get_global_step()
    optimiser = tf.train.MomentumOptimizer(
        learning_rate=params["learning_rate"],
        momentum=0.9)

    update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
    with tf.control_dependencies(update_ops):
        train_op = optimiser.minimize(loss, global_step=global_step)

    # 5. Return EstimatorSpec object
    return tf.estimator.EstimatorSpec(mode=mode,
                                      predictions=net_output_ops,
                                      loss=loss,
                                      train_op=train_op,
                                      eval_metric_ops=None)

def getDatasetInfo(folder):
    with open(os.path.join(folder, "dataset.json")) as f:
        data = json.load(f)
    return data["training"]

def splitArr(arr, fraction):
    arr1 = []
    arr2 = []
    length = len(arr)
    for i in range(length):
        if (i < length*fraction):
            arr1.append(arr[i])
        else:
            arr2.append(arr[i])
    return arr1, arr2

def train():
    modelPath = "./models"
    folder = "/home/vincent/Documents/imperial/individual project/datasets/decathlon/Task02_Heart"
    trainPaths = getDatasetInfo(folder)
    train_filenames, val_filenames = splitArr(trainPaths, 0.75)
    size = [33, 80, 80]
    readFn = readFunc(trainPaths, None, {"folder":folder, "depth":132, "size":size})
    #for i in range(len(trainPaths)):
    #    img = next(readFn)
    #    print("\n", img["features"]["x"].shape, img["labels"]["y"].shape, "\n")

    # Training parameters
    EVAL_EVERY_N_STEPS = 1
    EVAL_STEPS = 1
    NUM_CLASSES = 2
    NUM_CHANNELS = 1
    BATCH_SIZE = 1
    SHUFFLE_CACHE_SIZE = 2
    MAX_STEPS = 5000

    train_filenames = train_filenames[:2]
    val_filenames = val_filenames[:2]
    
    # Set up a data reader to handle the file i/o.
    reader_params = {'folder':folder, "depth":132, "size":size}
    reader = Reader(readFunc,
                    {'features': {'x': tf.float32},
                     'labels': {'y': tf.int32}})
    shape = {"features": {"x": size + [1]},
             "labels": {"y": size} }
    # Get input functions and queue initialisation hooks for training and
    # validation data
    train_input_fn, train_qinit_hook = reader.get_inputs(
        file_references=train_filenames,
        mode=tf.estimator.ModeKeys.TRAIN,
        example_shapes=shape,
        batch_size=BATCH_SIZE,
        shuffle_cache_size=SHUFFLE_CACHE_SIZE,
        params=reader_params)

    val_input_fn, val_qinit_hook = reader.get_inputs(
        file_references=val_filenames,
        mode=tf.estimator.ModeKeys.EVAL,
        example_shapes=shape,
        batch_size=BATCH_SIZE,
        shuffle_cache_size=SHUFFLE_CACHE_SIZE,
        params=reader_params)

        # Instantiate the neural network estimator
    nn = tf.estimator.Estimator(
        model_fn=model_fn,
        model_dir=modelPath,
        params={"learning_rate": 0.001, "numClasses":NUM_CLASSES},
        config=tf.estimator.RunConfig())

    # Hooks for validation summaries
    val_summary_hook = tf.contrib.training.SummaryAtEndHook(
        os.path.join(modelPath, 'eval'))
    step_cnt_hook = tf.train.StepCounterHook(
        every_n_steps=EVAL_EVERY_N_STEPS,
        output_dir=modelPath)

    print('Starting training...')
    try:
        for _ in range(MAX_STEPS // EVAL_EVERY_N_STEPS):
            print("Train")
            nn.train(
                input_fn=train_input_fn,
                hooks=[train_qinit_hook, step_cnt_hook],
                steps=EVAL_EVERY_N_STEPS)
            print("Validate")
            if True:
                results_val = nn.evaluate(
                    input_fn=val_input_fn,
                    hooks=[val_qinit_hook, val_summary_hook],
                    steps=EVAL_STEPS)
                print('Step = {}; val loss = {:.5f};'.format(
                    results_val['global_step'], results_val['loss']))

    except KeyboardInterrupt:
        pass

    print('Stopping now.')
    export_dir = nn.export_savedmodel(
        export_dir_base=modelPath,
        serving_input_receiver_fn=reader.serving_input_receiver_fn(reader_example_shapes))
    print('Model saved to {}.'.format(export_dir))
    

if __name__ == '__main__':
    np.random.seed(42)
    tf.set_random_seed(42)
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.logging.set_verbosity(tf.logging.ERROR)
    os.environ["CUDA_VISIBLE_DEVICES"] = '0'
    train()

# TODO:
# - Going to need to return smaller patches somehow us https://www.tensorflow.org/api_docs/python/tf/image/crop_and_resize to select boxes and re-size them to a given size - is this only for 2D images though???? Coudl use a for loop and numpy array manipulation
# - Memory allocation not even enough, need smaller patches so may aswell work on that now. Gonna need to iterate over the numpy array, storing maximal and minimal values of row, column and depth - building a square to preserve aspect ratio. Then we will need to resize it to a pre-agreed size.
# - OR, for now we just do a 3-D resize, halfing all dimensions post-padding... maybe test it on an ITK image first.
