import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
import random

#Simple Tensors
a = tf.constant([[1,2],[3,4]])
print(a)
a = tf.random.normal(shape=(10,3))
print(a)

print(a-a[0])
print(tf.exp(a)[0].numpy())

#Variables
s = tf.Variable(tf.zeros_like(a[0]))
for i in a:
    s.assign_add(i)
print(s)

tf.reduce_sum(a,axis=0)

#Computing Gradients
a = tf.random.normal(shape=(2, 2))
b = tf.random.normal(shape=(2, 2))

with tf.GradientTape() as tape:
    tape.watch(a)
    c = tf.sqrt(tf.square(a) + tf.square(b))
    dc_da = tape.gradient(c, a)
    print(dc_da)

#Example 1: Linear Regression
np.random.seed(13)

train_x = np.linspace(0, 3, 120)
train_labels = 2 * train_x + 0.9 + np.random.randn(*train_x.shape) * 0.5

plt.scatter(train_x, train_labels)
plt.show()

input_dim = 1
output_dim = 1
learning_rate = 0.1

#weight matrix
w = tf.Variable([[100.0]])
#bias vector
b = tf.Variable(tf.zeros(shape=(output_dim,)))

def f(x):
    return tf.matmul(x,w) + b
def compute_loss(labels, predictions):
    return tf.reduce_mean(tf.square(labels - predictions))

def train_on_batch(x, y):
    with tf.GradientTape() as tape:
        predictions = f(x)
        loss = compute_loss(y, predictions)
        dloss_dw, dloss_db = tape.gradient(loss, [w, b])
    w.assign_sub(learning_rate * dloss_dw)
    b.assign_sub(learning_rate * dloss_db)
    return loss

#shuffe the data
indices = np.random.permutation(len(train_x))
features = tf.constant(train_x[indices], dtype = tf.float32)
labels = tf.constant(train_labels[indices],dtype = tf.float32)

batch_size = 4
for epoch in range(10):
    for i in range(0, len(features), batch_size):
        loss = train_on_batch(tf.reshape(features[i:i+batch_size], (-1,1)), tf.reshape(labels[i:i+batch_size], (-1,1)))
    print('Epoch %d: last batch loss = %.4f' % (epoch, float(loss)))

w, b

plt.scatter(train_x, train_labels)
x = np.array([min(train_x), max(train_x)])
y = w.numpy()[0,0]*x+b.numpy()[0]
plt.plot(x,y,color='red')
plt.show()

#Computional Graph and GPU Computations

@tf.function
def train_on_batch(x,y):
    with tf.GradientTape() as tape:
        predictions = f(x)
        loss = compute_loss(y, predictions)
        dloss_dw, dloss_db = tape.gradient(loss, [w,b])
    w.assign_sub(learning_rate * dloss_dw)
    b.assign_sub(learning_rate * dloss_db)
    return loss
#code doesnt change at all but if it runs in a GPU and on a larger dataset-it would have a difference in speed
       
#Dataste API
w.assign([[10.0]])
b.assign([0.0])

dataset =  tf.data.Dataset.from_tensor_slices((train_x.astype(np.float32), train_labels.astype(np.float32)))
dataset = dataset.shuffle(buffer_size=1024).batch(256)

for epoch in range(10):
    for step, (x, y) in enumerate(dataset):
        loss = train_on_batch(tf.reshape(x,(-1,1)), tf.reshape(y,(-1,1)))
    print('Epoch %d: last batch loss = %.4f' % (epoch, float(loss)))

#Example 2: Classification
np.random.seed(0)

n = 100
X, Y = make_classification(n_samples=n, n_features=2, n_redundant=0, n_informative=2, flip_y=0.05, class_sep=1.5)

X = X.astype(np.float32)
Y = Y.astype(np.float32)

split = [70*n//100, (15+70)*n//100]
train_x, valid_x, test_x = np.split(X, split)
train_labels, valid_labels, test_labels = np.split(Y, split)

def plot_dataset(features, labels, W=None, b=None):
    fig, ax = plt.subplots(1,1)
    ax.set_xlabel('$x_i[0]$ -- (feature 1)')
    ax.set_ylabel('$x_i[1]$ -- (feature 2)')
    colors = ['r' if l else 'b' for l in labels]
    ax.scatter(features[:,0], features[:,1], marker='o', c=colors, s=100,alpha=0.5)
    if W is not None:
        min_x = min(features[:,0])
        max_x = max(features[:,1])
        min_y = min(features[:,1])*(1-.1)
        max_y = max(features[:,1])*(1+.1)
        cx = np.array([min_x, max_x], dtype=np.float32)
        cy = (0.5-W[0]*cx-b)/W[1]
        ax.plot(cx,cy,'g')
        ax.set_ylim(min_y,max_y)
    fig.show()
    plt.show()
plot_dataset(train_x,train_labels)

#NOrmalizing Data
train_x_norm = (train_x-np.min(train_x)) / (np.max(train_x)-np.min(train_x))
valid_x_norm = (valid_x-np.min(train_x)) / (np.max(train_x)-np.min(train_x))
test_x_norm = (test_x-np.min(train_x)) / (np.max(train_x)-np.min(train_x))

#training One-Layer Perceptron

W = tf.Variable(tf.random.normal(shape=(2,1)), dtype = tf.float32)
b = tf.Variable(tf.zeros(shape=(1,), dtype=tf.float32))

learning_rate = 0.1

@tf.function
def train_on_batch(x, y):
    with tf.GradientTape() as tape:
        z = tf.matmul(x, W) + b
        loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=y,logits=z))
    dloss_dw, dloss_db = tape.gradient(loss, [W, b])
    W.assign_sub(learning_rate * dloss_dw)
    b.assign_sub(learning_rate * dloss_db)
    return loss

dataset = tf.data.Dataset.from_tensor_slices((train_x_norm.astype(np.float32), train_labels.astype(np.float32)))
dataset = dataset.shuffle(128).batch(2)

for epoch in range(10):
    for step, (x, y) in enumerate(dataset):
        loss = train_on_batch(x, tf.expand_dims(y,1))
    print('Epoch %d: last batch loss = %.4f' % (epoch, float(loss)))
plot_dataset(train_x,train_labels, W.numpy(), b.numpy())

pred = tf.matmul(test_x,W)+b
fig,ax = plt.subplots(1,2)
ax[0].scatter(test_x[:,0],test_x[:,1],c=pred[:,0]>0.5)
ax[1].scatter(test_x[:,0],test_x[:,1],c=valid_labels)
plt.show()

tf.reduce_mean(tf.cast(((pred[0]>0.5)==test_labels),tf.float32))

#Using TensorFlow/Keras Optimizers

optimizer = tf.keras.optimizers.Adam(0.01)

W = tf.Variable(tf.random.normal(shape=(2,1)))
b = tf.Variable(tf.zeros(shape=(1,), dtype=tf.float32))

@tf.function
def train_on_batch(x, y):
    vars = [W, b]
    with tf.GradientTape() as tape:
        z = tf.sigmoid(tf.matmul(x, W) + b)
        loss = tf.reduce_mean(tf.keras.losses.binary_crossentropy(z,y))
        correct_prediction = tf.equal(tf.round(y), tf.round(z))
        acc = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        grads = tape.gradient(loss, vars)
        optimizer.apply_gradients(zip(grads, vars))
    return loss, acc
for epoch in range(20):
    for step, (x, y) in enumerate(dataset):
        loss, acc = train_on_batch(tf.reshape(x,(-1,2)), tf.reshape(y,(-1,1)))
    print('Epoch %d: last batch loss = %.4f, acc = %.4f' % (epoch, float(loss), acc))
    
#Functional API

inputs = tf.keras.Input(shape=(2,))
z = tf.keras.layers.Dense(1, kernel_initializer='glorot_uniform', activation='sigmoid')(inputs)
model = tf.keras.models.Model(inputs,z)

model.compile(optimizer=tf.keras.optimizers.Adam(0.1),
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.summary()
h = model.fit(train_x_norm, train_labels,batch_size=8, epochs=15)

plt.plot(h.history['accuracy'])
plt.show()

#Sequential API

model = tf.keras.models.Sequential()
model.add(tf.keras.layers.Dense(5,activation='sigmoid',input_shape=(2,)))
model.add(tf.keras.layers.Dense(1,activation='sigmoid'))

model.compile(optimizer=tf.keras.optimizers.Adam(0.1),
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.summary()
model.fit(train_x_norm,train_labels,validation_data=(test_x_norm,test_labels),batch_size=8,epochs=15)

plt.plot(h.history['accuracy'])
plt.show()

