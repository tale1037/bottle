import os
import random as rn
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# TensorFlow & Keras
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, Conv2D, InputLayer, Reshape, MaxPool2D, Flatten,
    Dropout, BatchNormalization
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # ✅ 从 tf.keras 导入，避免版本错乱

# 其他工具包
import cv2
from PIL import Image
from sklearn.model_selection import train_test_split