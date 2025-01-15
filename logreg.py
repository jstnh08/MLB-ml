import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn import linear_model, metrics
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score
)
from data_collection.databse import X, y, x_train_columns

"""
             Feature  Coefficient
9         away_win_p    -0.154376
6         home_win_p     0.127352
5  home_runs_allowed    -0.068096
0           home_era    -0.063445
3            away_ba    -0.055825
7   away_runs_scored    -0.044771
8  away_runs_allowed     0.039988
2            home_ba    -0.020331
1           away_era     0.010921
4   home_runs_scored     0.009232
Test set accuracy: 59.5
Confusion Matrix:
 [[62 33]
 [48 57]]
Accuracy Score: 0.595
Recall Score: 0.5428571428571428
Precision Score: 0.6333333333333333
F1 Score: 0.5846153846153846
"""

split_index = int(0.90 * len(X))
X_train, X_test = X[:split_index], X[split_index:]
print(len(X_train))
y_train, y_test = y[:split_index], y[split_index:]

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

reg = linear_model.LogisticRegression()

param_grid = {
    'C': [0.001, 0.01, 0.1, 1, 10, 100],
    'penalty': ['l2'],
    'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag'],
    'max_iter': [100, 200, 500],
    'class_weight': ['balanced', None]
}

grid_search = GridSearchCV(reg, param_grid, cv=5)
grid_search.fit(X_train_scaled, y_train)

print("Best Parameters:", grid_search.best_params_)

model = grid_search.best_estimator_

coefficients = model.coef_[0]

feature_importance = pd.DataFrame({
    'Feature': x_train_columns,
    'Coefficient': coefficients
})

feature_importance['Abs_Coefficient'] = feature_importance['Coefficient'].abs()
feature_importance = feature_importance.sort_values(by='Abs_Coefficient', ascending=False)

print(feature_importance[['Feature', 'Coefficient']])

y_pred = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, y_pred)
print("Test set accuracy:", accuracy * 100)
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

print("Accuracy Score:", accuracy_score(y_test, y_pred))
print("Recall Score:", recall_score(y_test, y_pred))
print("Precision Score:", precision_score(y_test, y_pred))
print("F1 Score:", f1_score(y_test, y_pred))
