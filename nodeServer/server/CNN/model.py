from keras.models import *
from keras.layers import *
from keras.optimizers import Adam, SGD
from keras.layers.merge import concatenate

from functools import partial


def create_convolution_block(input_layer, n_filters, batch_normalization=False, kernel=(3, 3, 3), activation=None, padding='same', strides=(1, 1, 1), instance_normalization=False):
    """
    :param strides:
    :param input_layer:
    :param n_filters:
    :param batch_normalization:
    :param kernel:
    :param activation: Keras activation layer to use. (default is 'relu')
    :param padding:
    :return:
    """
    layer = Conv3D(n_filters, kernel, padding=padding, strides=strides)(input_layer)
    if True:#batch_normalization:
        layer = BatchNormalization(axis=1)(layer)
    elif instance_normalization:
        try:
            from keras_contrib.layers.normalization import InstanceNormalization
        except ImportError:
            raise ImportError("Install keras_contrib in order to use instance normalization."
                              "\nTry: pip install git+https://www.github.com/farizrahman4u/keras-contrib.git")
        layer = InstanceNormalization(axis=1)(layer)
    if activation is None:
        return Activation('relu')(layer)
    else:
        return activation()(layer)

create_convolution_block = partial(create_convolution_block, activation=LeakyReLU, instance_normalization=True)


def weighted_dice_coefficient(y_true, y_pred, axis=(-3, -2, -1), smooth=0.00001):
    """
    Weighted dice coefficient. Default axis assumes a "channels first" data structure
    :param smooth:
    :param y_true:
    :param y_pred:
    :param axis:
    :return:
    """
    return K.mean(2. * (K.sum(y_true * y_pred,
                              axis=axis) + smooth/2)/(K.sum(y_true,
                                                            axis=axis) + K.sum(y_pred,
                                                                               axis=axis) + smooth))
def weightedDiceLoss(weighting, y_true, y_pred, axis=(-3, -2, -1), smooth=0.00001):
    return -K.mean(2. * (K.sum(y_true * y_pred * weighting,
                               axis=axis) + smooth/2)/(K.sum(y_true * weighting,
                                                             axis=axis) + K.sum(y_pred * weighting,
                                                                                axis=axis) + smooth))    

def weighted_dice_coefficient_loss(y_true, y_pred):
    return -weighted_dice_coefficient(y_true, y_pred)


def isensee2017_model(input_shape=(4, 128, 128, 128), n_base_filters=16, depth=5, dropout_rate=0.3,
                      n_segmentation_levels=3, n_labels=4, optimizer=Adam, initial_learning_rate=5e-4,
                      loss_function=weighted_dice_coefficient_loss, activation_name="sigmoid"):
    """
    This function builds a model proposed by Isensee et al. for the BRATS 2017 competition:
    https://www.cbica.upenn.edu/sbia/Spyridon.Bakas/MICCAI_BraTS/MICCAI_BraTS_2017_proceedings_shortPapers.pdf
    This network is highly similar to the model proposed by Kayalibay et al. "CNN-based Segmentation of Medical
    Imaging Data", 2017: https://arxiv.org/pdf/1701.03056.pdf
    :param input_shape:
    :param n_base_filters:
    :param depth:
    :param dropout_rate:
    :param n_segmentation_levels:
    :param n_labels:
    :param optimizer:
    :param initial_learning_rate:
    :param loss_function:
    :param activation_name:
    :return:
    """
    inputs = Input(input_shape)

    current_layer = inputs
    level_output_layers = list()
    level_filters = list()
    for level_number in range(depth):
        n_level_filters = (2**level_number) * n_base_filters
        level_filters.append(n_level_filters)

        if current_layer is inputs:
            in_conv = create_convolution_block(current_layer, n_level_filters)
        else:
            in_conv = create_convolution_block(current_layer, n_level_filters, strides=(2, 2, 2))

        context_output_layer = create_context_module(in_conv, n_level_filters, dropout_rate=dropout_rate)

        summation_layer = Add()([in_conv, context_output_layer])
        level_output_layers.append(summation_layer)
        current_layer = summation_layer

    segmentation_layers = list()
    for level_number in range(depth - 2, -1, -1):
        up_sampling = create_up_sampling_module(current_layer, level_filters[level_number])
        concatenation_layer = concatenate([level_output_layers[level_number], up_sampling], axis=1)
        localization_output = create_localization_module(concatenation_layer, level_filters[level_number])
        current_layer = localization_output
        if level_number < n_segmentation_levels:
            segmentation_layers.insert(0, Conv3D(n_labels, (1, 1, 1))(current_layer))

    output_layer = None
    for level_number in reversed(range(n_segmentation_levels)):
        segmentation_layer = segmentation_layers[level_number]
        if output_layer is None:
            output_layer = segmentation_layer
        else:
            output_layer = Add()([output_layer, segmentation_layer])

        if level_number > 0:
            output_layer = UpSampling3D(size=(2, 2, 2))(output_layer)

    activation_block = Activation(activation_name)(output_layer)

    model = Model(inputs=inputs, outputs=activation_block)
    model.compile(optimizer=optimizer(lr=initial_learning_rate), metrics=["accuracy", weighted_dice_coefficient_loss], loss=loss_function)
    return model


def create_localization_module(input_layer, n_filters):
    convolution1 = create_convolution_block(input_layer, n_filters)
    convolution2 = create_convolution_block(convolution1, n_filters, kernel=(1, 1, 1))
    return convolution2


def create_up_sampling_module(input_layer, n_filters, size=(2, 2, 2)):
    up_sample = UpSampling3D(size=size)(input_layer)
    convolution = create_convolution_block(up_sample, n_filters)
    return convolution


def create_context_module(input_layer, n_level_filters, dropout_rate=0.3, data_format="channels_first"):
    convolution1 = create_convolution_block(input_layer=input_layer, n_filters=n_level_filters)
    dropout = SpatialDropout3D(rate=dropout_rate, data_format=data_format)(convolution1)
    convolution2 = create_convolution_block(input_layer=dropout, n_filters=n_level_filters)
    return convolution2

def getUNet2(shape, nClasses, lr=5e-4, loss_function=weighted_dice_coefficient_loss, activation_name="sigmoid"):
    return isensee2017_model(input_shape=shape, n_labels=nClasses, initial_learning_rate=lr, loss_function=loss_function, activation_name="sigmoid")




## OLD ATTEMPTS


def getUNet(input_size):
    inputs = Input(input_size)

    activation = 'linear' 

    conv1 = Conv3D(32, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(inputs)
    act = LeakyReLU(alpha=0.1)(conv1)
    conv1 = Conv3D(64, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv1)
    pool1 = MaxPooling3D(pool_size=(2, 2, 2))(act)

    conv2 = Conv3D(64, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(pool1)
    act = LeakyReLU(alpha=0.1)(conv2)
    conv2 = Conv3D(128, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv2)
    pool2 = MaxPooling3D(pool_size=(2, 2, 2))(act)

    conv3 = Conv3D(128, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(pool2)
    act = LeakyReLU(alpha=0.1)(conv3)
    conv3 = Conv3D(256, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv3)
    pool3 = MaxPooling3D(pool_size=(2, 2, 2))(act)

    conv4 = Conv3D(256, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(pool3)
    act = LeakyReLU(alpha=0.1)(conv4)
    conv4 = Conv3D(256, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv4)
    drop4 = Dropout(0.5)(act)
    pool4 = MaxPooling3D(pool_size=(2, 2, 2))(drop4)

    conv5 = Conv3D(256, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(pool4)
    act = LeakyReLU(alpha=0.1)(conv5)
    conv5 = Conv3D(256, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv5)
    drop5 = Dropout(0.5)(act)

    up6 = Conv3D(128, 2, activation = activation, padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2,2))(drop5))
    act = LeakyReLU(alpha=0.1)(up6)
    merge6 = merge([drop4,act], mode = 'concat', concat_axis = 4)
    conv6 = Conv3D(128, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(merge6)
    act = LeakyReLU(alpha=0.1)(conv6)
    conv6 = Conv3D(128, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv6)
    
    up7 = Conv3D(128, 2, activation = activation, padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2,2))(act))
    act = LeakyReLU(alpha=0.1)(up7)
    merge7 = merge([conv3,act], mode = 'concat', concat_axis = 4)
    conv7 = Conv3D(128, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(merge7)
    act = LeakyReLU(alpha=0.1)(conv7)
    conv7 = Conv3D(128, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv7)

    up8 = Conv3D(64, 2, activation = activation, padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2,2))(act))
    act = LeakyReLU(alpha=0.1)(up8)
    merge8 = merge([conv2,act], mode = 'concat', concat_axis = 4)
    conv8 = Conv3D(64, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(merge8)
    act = LeakyReLU(alpha=0.1)(conv8)
    conv8 = Conv3D(64, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv8)

    up9 = Conv3D(64, 2, activation = activation, padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2,2))(act))
    act = LeakyReLU(alpha=0.1)(up9)
    merge9 = merge([conv1,act], mode = 'concat', concat_axis = 4)
    conv9 = Conv3D(32, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(merge9)
    act = LeakyReLU(alpha=0.1)(conv9)
    conv9 = Conv3D(32, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv9)
    conv9 = Conv3D(2, 3, activation = activation, padding = 'same',
                   kernel_initializer = 'he_normal')(act)
    act = LeakyReLU(alpha=0.1)(conv9)
    conv10 = Conv3D(1, 1, activation = 'sigmoid')(act)

    model = Model(input = inputs, output = conv10)

    adam = Adam(lr = 5e-4)
    sgd = optimizers.SGD(lr=0.001, decay=1.2e-2, momentum=0.9, nesterov=True)
    model.compile(optimizer = sgd, loss = 'binary_crossentropy', metrics = ['accuracy'])
    return model


def getPCNet(input_size):
    inputs = Input(input_size)

    conv1 = Conv3D(64, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(inputs)
    conv1 = Conv3D(64, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv1)

    conv2 = Conv3D(64, 3, dilation_rate=2, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv1)
    conv2 = Conv3D(64, 3, dilation_rate=2, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv2)

    conv3 = Conv3D(64, 3, dilation_rate=3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv2)
    conv3 = Conv3D(64, 3, dilation_rate=3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv3)

    conv4 = Conv3D(64, 3, dilation_rate=4, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv3)
    conv4 = Conv3D(64, 3, dilation_rate=4, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv4)

    merge1 = merge([conv1,conv2,conv3,conv4], mode = 'concat', concat_axis = 4)
    conv10 = Conv3D(1, 1, activation = 'sigmoid')(merge1)

    model = Model(input = inputs, output = conv10)

    adam = Adam(lr = 1e-4)
    sgd = SGD(lr=0.001, decay=1.2e-2, momentum=0.9, nesterov=True)
    model.compile(optimizer = adam, loss = 'binary_crossentropy', metrics = ['accuracy'])
    return model

