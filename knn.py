import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import pickle


df = pd.read_csv('color/colors.csv')


color_mapping = {
    'RED': 0,
    'GREEN': 1,
    'BLUE': 2,
    'ORANGE': 3,
    'BROWN': 4,
    'PURPLE': 5,
    'BLACK': 6,
    'WHITE': 7
}

df['class'] = df['class'].map(color_mapping)

X = np.array(df[['r', 'g', 'b']])

y = df['class'].values


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)

pickle.dump(knn, open("knn_pickle", "wb"))
knn_model = pickle.load(open("knn_pickle", "rb"))
test_prediction = knn_model.predict(np.array([[120, 50, 200]]))[0]
for class_id, color in enumerate(color_mapping):
    if color_mapping[color] == test_prediction:
        print(color)
        break

accuracy = knn_model.score(X_test, y_test)
print(f'Accuracy: {accuracy * 100:.2f}%')
