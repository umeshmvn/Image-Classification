# -*- coding: utf-8 -*-
"""venkata_naga_umesh_munagala_python_code_assignment4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1TtJWur9-JIi20w9nyQalNnSjEuuVvc0J
"""

import torch
import torch.nn as nn
from enum import Enum
import matplotlib.pyplot as plt
# Enum to allocate different modes
class Modes(Enum):
    MODE_1 = "1"
    MODE_2 = "2"

class ConvNet(nn.Module):
    def __init__(self, mode):
        super(ConvNet, self).__init__()
        self.mode = mode
        self.layers = []
        # The Common layers taken by all modes
        common_layers = [
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        ]
        # precise layers for each mode
        specific_layers = {
            Modes.MODE_1: [
                nn.Dropout(0.2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Conv2d(64, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Dropout(0.2),
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Flatten(),
                nn.Linear(128*8*8, 128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, 10)
            ],
            Modes.MODE_2: [
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Conv2d(64, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Conv2d(128, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Conv2d(128, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.Flatten(),
                nn.Linear(128*8*8, 128),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(128, 10)
            ]
        }
        #Merge the layers that are common across all modes with those that are specific to the selected mode.
        self.layers = common_layers + specific_layers.get(Modes(self.mode), [])
        #Building the neural network model using the Sequential container
        self.model = nn.Sequential(*self.layers)

    def forward(self, X):
        return self.model(X)


with torch.no_grad():
    #Create an instance of ConvNet with MODE_1 as the chosen mode
    model = ConvNet(mode=Modes.MODE_1.value)
    output_shape = model(torch.rand(1, 3, 32, 32)).shape
#Output and display the shape of the model's result
print(output_shape)

from __future__ import print_function
import argparse
import os
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torch.utils.tensorboard import SummaryWriter
import argparse
import numpy as np

def train(model, device, train_loader, optimizer, criterion, epoch, batch_size):
    '''
    Trains the model for an epoch and optimizes it.
    model: The model to train. Should already be in correct device.
    device: 'cuda' or 'cpu'.
    train_loader: dataloader for training samples.
    optimizer: optimizer to use for model parameter updates.
    criterion: used to compute loss for prediction and target
    epoch: Current epoch to train for.
    batch_size: Batch size to be used.
    '''

    # Set model to train mode before each epoch
    model.train()

    # Empty list to store losses
    losses = []
    correct = 0

    # Iterate over entire training samples (1 epoch)
    for batch_idx, batch_sample in enumerate(train_loader):
        data, target = batch_sample

        # Push data/label to correct device
        data, target = data.to(device), target.to(device)

        # Reset optimizer gradients. Avoids grad accumulation (accumulation used in RNN).
        optimizer.zero_grad()

        # Do forward pass for current set of data
        output = model(data)

        # ======================================================================
        # Compute loss based on criterion
        # ----------------- YOUR CODE HERE ----------------------
        #
        # Remove NotImplementedError and assign correct loss function.
        loss = criterion(output, target)

        # Computes gradient based on final loss
        loss.backward()

        # Store loss
        losses.append(loss.item())

        # Optimize model parameters based on learning rate and gradient
        optimizer.step()

        # Get predicted index by selecting maximum log-probability
        pred = output.argmax(dim=1, keepdim=True)

        # ======================================================================
        # Count correct predictions overall
        # ----------------- YOUR CODE HERE ----------------------
        #
        # Remove NotImplementedError and assign counting function for correct predictions.
        correct += torch.sum(pred==target.reshape(-1,1)).item()
    #Determine the average training loss, total number of samples in the training set, and compute the training accuracy.
    train_loss = np.mean(losses)
    total_samples = (batch_idx + 1) * batch_size
    train_acc = correct / total_samples
    #Create and display messages regarding the average training loss and accuracy.
    avg_loss_message = 'Train set: Average loss: {:.4f}'.format(train_loss)
    acc_message = 'Accuracy: {}/{} ({:.0f}%)'.format(correct, total_samples, 100. * train_acc)
    print('\n'.join([avg_loss_message, acc_message]))
    return train_loss, train_acc



def test(model, device, test_loader):
    '''
    Tests the model.
    model: The model to train. Should already be in correct device.
    device: 'cuda' or 'cpu'.
    test_loader: dataloader for test samples.
    '''

    # Set model to eval mode to notify all layers.
    model.eval()

    losses = []
    correct = 0

    # Set torch.no_grad() to disable gradient computation and backpropagation
    with torch.no_grad():
        for batch_idx, sample in enumerate(test_loader):
            data, target = sample
            data, target = data.to(device), target.to(device)


            # Predict for data by doing forward pass
            output = model(data)

            # ======================================================================
            # Compute loss based on same criterion as training
            # ----------------- YOUR CODE HERE ----------------------
            #
            # Remove NotImplementedError and assign correct loss function.
            # Compute loss based on same criterion as training
            loss = F.cross_entropy(output, target=target)

            # Append loss to overall test loss
            losses.append(loss.item())

            # Get predicted index by selecting maximum log-probability
            pred = output.argmax(dim=1, keepdim=True)

            # ======================================================================
            # Count correct predictions overall
            # ----------------- YOUR CODE HERE ----------------------
            #
            # Remove NotImplementedError and assign counting function for correct predictions.
            correct += torch.sum(pred==target.reshape(-1,1)).item()
    #Compute the mean test loss.
    test_loss = np.mean(losses)
    total_samples = len(test_loader.dataset)
    accuracy = 100. * correct / total_samples
    #Compose a message expressing the average test loss.
    avg_loss_message = 'Test set: Average loss: {:.4f}'.format(test_loss)
    #Generate a message conveying the accuracy information.
    acc_message = 'Accuracy: {}/{} ({:.0f}%)'.format(correct, total_samples, accuracy)
    print('\n'.join([avg_loss_message, acc_message]))
    # Returns the test loss and accuracy
    return test_loss, accuracy


def run_main(mode, learning_rate, batch_size, num_epochs):
    # Check if cuda is available
    use_cuda = torch.cuda.is_available()

    # Set proper device based on cuda availability
    device = torch.device("cuda" if use_cuda else "cpu")
    print("Torch device selected: ", device)

    # Initialize the model and send to device
    model = ConvNet(mode).to(device)

    # ======================================================================
    # Define loss function.
    # ----------------- YOUR CODE HERE ----------------------
    #
    # Remove NotImplementedError and assign correct loss function.
    criterion = nn.CrossEntropyLoss()

    # ======================================================================
    # Define optimizer function.
    # ----------------- YOUR CODE HERE ----------------------
    #
    # Remove NotImplementedError and assign appropriate optimizer with learning rate and other paramters.
    optimizer = optim.SGD(params=model.parameters(), lr=learning_rate)


    # Create transformations to apply to each data sample
    # Can specify variations such as image flip, color flip, random crop, ...
    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.0,), (1.0,))
        ])

    # Load datasets for training and testing
    # Inbuilt datasets available in torchvision (check documentation online)
    dataset1 = datasets.CIFAR10('./data/', train=True, download=True,
                       transform=transform)
    dataset2 = datasets.CIFAR10('./data/', train=False,
                       transform=transform)
    train_loader = DataLoader(dataset1, batch_size = batch_size,
                                shuffle=True, num_workers=2)
    test_loader = DataLoader(dataset2, batch_size = batch_size,
                                shuffle=False, num_workers=2)

    best_accuracy = 0.0

    # Run training for n_epochs specified in config
    losses = []
    accuracy = []
    epoch = 1
    best_accuracy = 0.0

    while epoch <= num_epochs:
        #Train the model for a single epoch and retrieve the training loss and accuracy.
        train_loss, train_accuracy = train(model, device, train_loader, optimizer, criterion, epoch, batch_size)
        test_loss, test_accuracy = test(model, device, test_loader)
        #Add the training and test losses to the 'losses' list.
        losses.append({"train_loss": train_loss, "test_loss": test_loss})
        #Add the training and test accuracies to the 'accuracy' list. If the current test accuracy is greater, update the best accuracy.
        accuracy.append({"train_accuracy": train_accuracy, "test_accuracy": test_accuracy})

        best_accuracy = max(best_accuracy, test_accuracy)
        #incremented the epoch value
        epoch += 1

    print("accuracy is {:2.2f}".format(best_accuracy))
    print("Training and evaluation finished")
    return model, losses, accuracy

model, losses, accuracy = run_main(mode="1", learning_rate=0.05, batch_size=32, num_epochs=30)

train_acc = []
test_acc = []
for i in range(len(accuracy)):
    #Add the normalized test accuracy, obtained by dividing it by 100, to the 'test_acc' list.
    test_acc.append(accuracy[i]['test_accuracy']/100)
    #Add the training accuracy to the 'train_acc' list.
    train_acc.append(accuracy[i]['train_accuracy'])

plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1).set_title("Accuracy Train vs Test")

# Using different colors and markers
plt.plot(train_acc, label="Training Accuracy", color="blue", marker='o')
plt.plot(test_acc, label="Testing Accuracy", color="orange", marker='s')

plt.legend()
plt.show()
#The code utilizes a lambda function and the map operation to collect training losses from the 'losses' list.
train_loss = list(map(lambda x: x['train_loss'], losses))
##The code utilizes a lambda function and the map operation to collect testing losses from the 'losses' list.
test_loss = list(map(lambda x: x['test_loss'], losses))


plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1).set_title("Loss Train vs Test")

# Using different colors and markers
plt.plot(train_loss, label="Training Losses", color="blue", marker='o')
plt.plot(test_loss, label="Testing Losses", color="orange", marker='s')

plt.legend()
plt.show()

model, losses, accuracy = run_main(mode="2", learning_rate=0.05, batch_size=32, num_epochs=30)

#Collect training accuracies from the 'accuracy' list by applying a lambda function and using the map operation.
train_acc = list(map(lambda x: x['train_accuracy'], accuracy))
#Obtain normalized test accuracies from the 'accuracy' list by dividing each 'test_accuracy' value by 100 using a lambda function and map.
test_acc = list(map(lambda x: x['test_accuracy'] / 100, accuracy))


plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1).set_title("Accuracy Train vs Test")

# Using different colors and markers
plt.plot(train_acc, label="Training Accuracy", color="purple", marker='o')
plt.plot(test_acc, label="Testing Accuracy", color="cyan", marker='s')

plt.legend()
plt.show()

#Gather training losses from the 'losses' list using a lambda function and the map operation.
train_loss = list(map(lambda x: x['train_loss'], losses))
#Retrieve test losses from the 'losses' list by employing a lambda function and the map operation.
test_loss = list(map(lambda x: x['test_loss'], losses))

plt.figure(figsize=(20, 10))

plt.subplot(1, 2, 1).set_title("Loss Train vs Test")

# Using different colors and markers
plt.plot(train_loss, label="Training Losses", color="purple", marker='o')
plt.plot(test_loss, label="Testing Losses", color="cyan", marker='s')

plt.legend()
plt.show()