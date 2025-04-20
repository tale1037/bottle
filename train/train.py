import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import glob
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import img_to_array, ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import tensorflow as tf

# 加载图像
def load_images_from_folder(folder, label_value, resize=(256,256), rotate=False):
    images = []
    labels = []
    for img_path in glob.glob(folder + "/*.jpeg") + glob.glob(folder + "/*.png") + glob.glob(folder + "/*.jpg"):
        img = cv2.imread(img_path)
        img = Image.fromarray(img, 'RGB').resize(resize)
        if rotate:
            images.extend([img, img.rotate(15), img.rotate(-15)])
            labels.extend([label_value]*3)
        else:
            images.append(img)
            labels.append(label_value)
    return images, labels

full, label1 = load_images_from_folder("../dataset/Full  Water level/Full  Water level", 0)
empty, label2 = load_images_from_folder("../dataset/Empty", 1, rotate=True)

print(len(empty), len(label2))
img = np.array([img_to_array(i)/255.0 for i in (full + empty)])
label = np.array(label1 + label2)

# 划分训练测试
x_train, x_test, y_train, y_test = train_test_split(img, label, test_size=0.25, random_state=42, stratify=label)

# One-hot 编码
y_train_cat = to_categorical(y_train, num_classes=2)
y_test_cat = to_categorical(y_test, num_classes=2)

# 实时增强
train_datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
train_generator = train_datagen.flow(x_train, y_train_cat, batch_size=32)

# 验证集只做 rescale
val_datagen = ImageDataGenerator()
val_generator = val_datagen.flow(x_test, y_test_cat, batch_size=32)

# MobileNetV2 模型
base_model = MobileNetV2(input_shape=(256,256,3), include_top=False, weights='imagenet')
base_model.trainable = False

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.3),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(2, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 回调函数
callbacks = [
    EarlyStopping(patience=5, monitor='val_loss', restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', patience=2, factor=0.5, verbose=1)
]

# 训练
history = model.fit(train_generator, validation_data=val_generator, epochs=50, callbacks=callbacks)

# 评估
model.evaluate(val_generator)

# 可视化结果
plt.plot(history.history['accuracy'], label='Train Acc', color='red')
plt.plot(history.history['val_accuracy'], label='Val Acc', color='green')
plt.title("Training History")
plt.legend()
plt.show()

# 保存模型
model.save("./savedmodels/MobileNetV2_transfer_model.h5")
