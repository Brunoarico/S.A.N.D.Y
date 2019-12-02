import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

df = pd.read_csv('../training.csv')

#create a dataframe with all training data except the target column
X = df.drop(columns=['Class'])
y = df['Class'].values
print("X_size: ", X.shape, "Y_size: ", y.shape)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1, stratify=y)



knn = KNeighborsClassifier(n_neighbors = 3)

'''knn.fit(X_train, y_train)
print(df)
print(knn.predict(X_test)[0:5])

knn = KNeighborsClassifier(n_neighbors=3)#train model with cv of 5
cv_scores = cross_val_score(knn, X, y, cv=5)#print each cv score (accuracy) and average them
print(cv_scores)
print('cv_scores mean:{}'.format(np.mean(cv_scores)))'''

param_grid = {'n_neighbors': np.arange(1, 25)}#use gridsearch to test all values for n_neighbors
knn_gscv = GridSearchCV(knn, param_grid, cv=5)#fit model to data
knn_gscv.fit(X, y)

print(knn_gscv.best_params_)
