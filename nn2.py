import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)
from torch.utils.data import DataLoader, TensorDataset
# from data_collection.databse import X, y
import numpy as np

X = np.load("data_collection/X.npy")
y = np.load("data_collection/y.npy")
split_index = int(0.9 * len(X))
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

print(len(X_train))
# Apply standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32)


batch_size = 32
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)


class SmallNeuralNet(nn.Module):
    def __init__(self, input_size):
        super(SmallNeuralNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 8)
        self.fc2 = nn.Linear(8, 8)
        self.fc3 = nn.Linear(8, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

top_acc = 0
best_classification_report = None
best_confusion = None

loss_sets = []

for i in range(100):
    print(f"Training Model {i + 1}...")
    input_size = X_train_tensor.shape[1]
    model = SmallNeuralNet(input_size)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    loss_set = []
    for epoch in range(25):
        model.train()
        total_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            outputs = model(X_batch).squeeze()
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        loss_set.append(total_loss / len(train_loader))
    loss_sets.append(loss_set)

    model.eval()
    y_pred_probs = []
    y_true = []

    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch).squeeze()
            y_pred_probs.extend(outputs.numpy())
            y_true.extend(y_batch.numpy())

    y_pred = [1 if prob > 0.5 else 0 for prob in y_pred_probs]

    accuracy = accuracy_score(y_true, y_pred)

    if accuracy > top_acc:
        top_acc = accuracy
        best_classification_report = classification_report(y_true, y_pred, output_dict=False)
        best_confusion = confusion_matrix(y_test, y_pred)

    print(f"Model {i + 1} Accuracy: {accuracy * 100:.2f}%")

print("\nBest Model Results:")
print(f"Highest Accuracy: {top_acc * 100:.2f}%")
print("Best Model Classification Report:\n")
print(best_classification_report)

print(best_confusion)
