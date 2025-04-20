import glob
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras import models, layers
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model


model = load_model("./train/savedmodels/MobileNetV2_transfer_model.h5")

labels = np.array(["full", "empty"])
label_dict = {i: labels[i] for i in range(len(labels))}


def preprocess_image_cv(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img, mode='RGB')
    img_pil = img_pil.resize((256, 256))
    img_array = np.array(img_pil) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)
    return img_batch, img_pil  # 返回：模型输入、用于显示的 PIL 图像

# # 获取所有图片路径
# img_paths = glob.glob("../dataset/Empty/*.jpg")
# size = len(img_paths)
#
# # 每行显示 5 张图
# cols = 5
# rows = (size + cols - 1) // cols
# plt.figure(figsize=(cols * 4, rows * 4))
#
# for i, img_path in enumerate(img_paths):
#     img_batch, img_for_show = preprocess_image_cv(img_path)
#     y_pred = model.predict(img_batch)
#     k = np.argmax(y_pred[0])
#     conf = y_pred[0][k]  # 获取最大概率（置信度）
#     label = label_dict[k]  # 标签名称
#     title_text = f"{label} ({conf * 100:.1f}%)"  # 保留一位小数
#     plt.subplot(rows, cols, i + 1)
#     plt.imshow(img_for_show)
#     plt.axis('off')
#     plt.title(title_text, color='green')
#
# plt.tight_layout()
# plt.show()


def predictbypath(path):
    img_batch, img_for_show = preprocess_image_cv(path)
    y_pred = model.predict(img_batch)
    k = np.argmax(y_pred[0])
    conf = y_pred[0][k]  # 获取最大概率（置信度）
    label = label_dict[k]  # 标签名称
    return conf,label