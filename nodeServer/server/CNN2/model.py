from keras.models import *
from keras.layers import *
from keras.optimizers import Adam


def getUnet():
    inputs = Input(input_size)
    conv1 = Conv3D(32, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(inputs)
    conv1 = Conv3D(64, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv1)
    pool1 = MaxPooling3D(pool_size=(2, 2, 2))(conv1)

    conv2 = Conv3D(64, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(pool1)
    conv2 = Conv3D(128, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv2)
    pool2 = MaxPooling3D(pool_size=(2, 2, 2))(conv2)

    conv3 = Conv3D(128, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(pool2)
    conv3 = Conv3D(256, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv3)
    pool3 = MaxPooling3D(pool_size=(2, 2, 2))(conv3)

    conv4 = Conv3D(256, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(pool3)
    conv4 = Conv3D(256, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv4)
    drop4 = Dropout(0.5)(conv4)
    pool4 = MaxPooling3D(pool_size=(2, 2, 2))(drop4)

    conv5 = Conv3D(256, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(pool4)
    conv5 = Conv3D(256, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv5)
    drop5 = Dropout(0.5)(conv5)

    up6 = Conv3D(128, 2, activation = 'relu', padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2))(drop5))
    merge6 = merge([drop4,up6], mode = 'concat', concat_axis = 3)
    conv6 = Conv3D(128, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(merge6)
    conv6 = Conv3D(128, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv6)

    up7 = Conv3D(128, 2, activation = 'relu', padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2))(conv6))
    merge7 = merge([conv3,up7], mode = 'concat', concat_axis = 3)
    conv7 = Conv3D(128, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(merge7)
    conv7 = Conv3D(128, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv7)

    up8 = Conv3D(64, 2, activation = 'relu', padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2))(conv7))
    merge8 = merge([conv2,up8], mode = 'concat', concat_axis = 3)
    conv8 = Conv3D(64, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(merge8)
    conv8 = Conv3D(64, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv8)

    up9 = Conv3D(64, 2, activation = 'relu', padding = 'same',
                 kernel_initializer = 'he_normal')(UpSampling3D(size = (2,2))(conv8))
    merge9 = merge([conv1,up9], mode = 'concat', concat_axis = 3)
    conv9 = Conv3D(32, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(merge9)
    conv9 = Conv3D(32, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv9)
    conv9 = Conv3D(2, 3, activation = 'relu', padding = 'same',
                   kernel_initializer = 'he_normal')(conv9)
    conv10 = Conv3D(1, 1, activation = 'sigmoid')(conv9)

    model = Model(input = inputs, output = conv10)

    model.compile(optimizer = Adam(lr = 1e-4), loss = 'binary_crossentropy', metrics = ['accuracy'])
    return model
    
# Question of inputs:
# - Either have no input size, but I still need images to be divisible by pool^depth
# - OR have no input size, and alter things with padding if/when they aren't divisible
# - OR have a set input size, and rescale images to this size
# 3rd option is ok if I go with bounding-box, which seems to be the way to go

# BIG PICTURE:
# - CNN on server is just trained in basic segmentation
# - People can upload a dataset to fine-tune the network - here the bounding-box is done automatically
# - Then they can upload live data, doing the bounding-box themselves.
    
