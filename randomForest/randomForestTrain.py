from typing import Dict, List, Tuple
import random

import numpy as np
import pandas as pd
import string
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import text
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

TRUE_PAIR = float(1)
FALSE_PAIR = float(0)

class Dataset:
    def __init__(self) -> None:
        self.x = []
        self.y: List[float] = []

    def __len__(self) -> int:
        return len(self.y)
    
    def addPair(self, a, b, label: int) -> None:
        pair = np.concatenate((a, b), axis=None)
        reversePair = np.concatenate((a, b), axis=None)

        # https://stackoverflow.com/questions/14446128/python-append-vs-extend-efficiency
        self.x.extend((pair, reversePair))
        self.y.extend((label, label))


print("Importing data.")
X_filepath = "./X1.csv"
Y_filepath = "./Y1.csv"
X = pd.read_csv(X_filepath)
Y = pd.read_csv(Y_filepath)
X_fixed = X.drop(columns=['id'])
X_fixed.fillna(" ", inplace=True)
X_sum = [' '.join([j[:100] for j in X_fixed.iloc[i]]) for i in range(X_fixed.shape[0])]
X_sum = [i.translate(str.maketrans('', '', string.punctuation)) for i in X_sum]

print("Vectorize data.")
vectorizer = text.TfidfVectorizer(max_df=0.9, stop_words=text.ENGLISH_STOP_WORDS)
X_tfidf = vectorizer.fit_transform(X_sum).toarray()
print(X_tfidf[0].shape)

print("Create pair values.")
idsToIndexes = {}
for index, i in X.iterrows():
    idsToIndexes[i["id"]] = index

trainDataset = Dataset()

possiblePairs: Dict[Tuple[int, int], float] = {}

# Y does not have all the possible pairs, only the *true pairs*
for index, i in Y.iterrows():
    left = idsToIndexes[i["lid"]]
    right = idsToIndexes[i["rid"]]
    
    possiblePairs[(left, right)] = TRUE_PAIR

numTruePairs = len(possiblePairs)
while len(possiblePairs) < 2*numTruePairs:
    i = random.randint(0, X.shape[0] - 2)
    j = random.randint(i + 1, X.shape[0] - 1)

    if (i, j) not in possiblePairs:
        possiblePairs[(i, j)] = FALSE_PAIR

while len(possiblePairs) > 0:
    pair, label = possiblePairs.popitem()
    trainDataset.addPair(X_tfidf[pair[0]], X_tfidf[pair[1]], label)

# X_pairs = possiblePairs.keys()
# y = possiblePairs.values()
X_pairs = trainDataset.x
y = trainDataset.y

print("Separate into train and test data.")
X_train, X_test, y_train, y_test = train_test_split(X_pairs, y, test_size=0.1, random_state=42)

print("Train classifier.")
classifier = RandomForestClassifier(verbose=2, class_weight={FALSE_PAIR:0.01, TRUE_PAIR:100.0},
                                    n_jobs=-1, random_state=42)
classifier.fit(X_train, y_train) 

print("Make prediction.")
y_pred = classifier.predict(X_test)
print(confusion_matrix(y_test,y_pred))
print(classification_report(y_test,y_pred))
print(accuracy_score(y_test, y_pred))

print("Save classifier")
joblib.dump(classifier, "./classifier.txt", compress=3)
