import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)
# from data_collection.databse import X, y, x_train_columns
import numpy as np

x_train_columns = ['home_era', 'away_era', 'home_ba', 'away_ba', 'home_runs_scored', 'home_runs_allowed', 'home_win_p', 'away_runs_scored', 'away_runs_allowed', 'away_win_p']

X = np.load("data_collection/X.npy")
y = np.load("data_collection/y.npy")
split_index = int(0.9 * len(X))
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

print("hall")
# scaler = StandardScaler()
# X_train_scaled = scaler.fit_transform(X_train)  # Fit and transform on the training set
# X_test_scaled = scaler.transform(X_test)        # Only transform on the test set

rf = RandomForestClassifier(random_state=42)

param_grid = {
    'n_estimators': [50, 100],               # Number of trees in the forest
    'max_depth': [10, 20],              # Maximum depth of each tree
    'min_samples_split': [2, 5, 10],              # Minimum samples required to split an internal node
    'min_samples_leaf': [1, 2, 4],                # Minimum samples required to be at a leaf node
    'class_weight': ['balanced', None],           # Adjust weights for class imbalance
    'bootstrap': [True, False]                    # Use bootstrap samples when building trees
}

print("did those")
grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
print("typeeee")
print("Best Parameters:", grid_search.best_params_)

model = grid_search.best_estimator_

feature_importance = pd.DataFrame({
    'Feature': x_train_columns,
    'Importance': model.feature_importances_
})

feature_importance = feature_importance.sort_values(by='Importance', ascending=False)

print(feature_importance[['Feature', 'Importance']])

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Test set accuracy:", accuracy * 100)
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("Accuracy Score:", accuracy_score(y_test, y_pred))
print("Recall Score:", recall_score(y_test, y_pred))
print("Precision Score:", precision_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))