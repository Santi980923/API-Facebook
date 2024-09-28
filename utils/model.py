import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split

df = pd.read_excel('C:/API-FACEBOOK/API-Facebook/data/BBDD.xlsx')


df = df[['sentimiento', 'review_es']].copy()

df['sentimiento'].hist()

target_map = {'positivo': 1, 'negativo': 0}
df['target'] = df['sentimiento'].map(target_map)

df_train, df_test = train_test_split(df)

vectorizer = TfidfVectorizer(max_features=2000)

X_train = vectorizer.fit_transform(df_train['review_es'])

X_test = vectorizer.transform(df_test['review_es'])

Y_train = df_train['target']
Y_test = df_test['target']

model = LogisticRegression(max_iter=1000)
model.fit(X_train, Y_train)
print("Train acc:", model.score(X_train, Y_train))
print("Test acc:", model.score(X_test, Y_test))

P_train = model.predict(X_train)
P_test = model.predict(X_test)

P_train = model.predict(X_train)
P_test = model.predict(X_test)

cm = confusion_matrix(Y_train, P_train, normalize='true')

def plot_cm(cm):
    classes = ['negativo', 'positivo']
    df_cm = pd.DataFrame(cm, index=classes, columns=classes)
    ax = sn.heatmap(df_cm, annot=True, fmt='g')
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Objetivo")

cm = confusion_matrix(Y_test, P_test, normalize='true')

word_index_map = vectorizer.vocabulary_

model.coef_[0]

corte = 4

print("Palabras más positivas:")
for word, index in word_index_map.items():
    weight = model.coef_[0][index]
    if weight > corte:
        print(word, weight)

print("Palabras más negativas:")
for word, index in word_index_map.items():
    weight = model.coef_[0][index]
    if weight < -corte:
        print(word, weight)

prueba = ["", "estuvo terrible la película, me aburrí mucho", "no la recomiendo", "la"]

# Transformar la entrada con el vectorizador
x = vectorizer.transform(prueba)

# Predecir con el modelo
P = model.predict(x)

# Obtener las clases del modelo
clases = model.classes_

# Mostrar la clase predicha
for i in range (len(prueba)):
    if clases[P[i]] == 0:
        print(f"el Comentario: '{prueba[i]}' es: Negativo")
    else:
        print(f"el Comentario: '{prueba[i]}' es: Positivo")
