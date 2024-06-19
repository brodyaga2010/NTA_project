import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import numpy as np
import joblib

def printRes(y_test, y_pred):
    # Оценка модели
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print(f'Accuracy: {accuracy}')
    print('Classification Report:')
    print(report)

def printFeatureImportances(model, vectorizer):
    feature_names = vectorizer.get_feature_names_out()
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    print("Feature importances:")
    for i in range(10):
        print(f"{i + 1}. Feature {feature_names[indices[i]]} ({importances[indices[i]]})")

def vectorising(X_test, X_test_val, X_train):
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    X_test_val_tfidf = vectorizer.transform(X_test_val)
    return X_test_tfidf, X_test_val_tfidf, X_train_tfidf, vectorizer

def randomForestModel(X_train_tfidf, y_train, X_test_tfidf, y_test, X_test_val_tfidf, y_test_val):
    model = RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=5, random_state=42)

    # Обучение модели
    model.fit(X_train_tfidf, y_train)

    print('Предсказание на тестовых данных:')
    y_pred = model.predict(X_test_tfidf)
    printRes(y_test, y_pred)

    print('Предсказание на валидирующих данных:')
    y_pred_val = model.predict(X_test_val_tfidf)
    printRes(y_test_val, y_pred_val)

    return model

def gradientBoostingModel(X_train_tfidf, y_train, X_test_tfidf, y_test, X_test_val_tfidf, y_test_val):
    model = GradientBoostingClassifier(n_estimators=200, max_depth=3, min_samples_split=5, random_state=42)

    # Обучение модели
    model.fit(X_train_tfidf, y_train)

    print('Предсказание на тестовых данных:')
    y_pred = model.predict(X_test_tfidf)
    printRes(y_test, y_pred)

    print('Предсказание на валидирующих данных:')
    y_pred_val = model.predict(X_test_val_tfidf)
    printRes(y_test_val, y_pred_val)

    return model

def adaBoostingModel(X_train_tfidf, y_train, X_test_tfidf, y_test, X_test_val_tfidf, y_test_val):
    model = AdaBoostClassifier(n_estimators=200, random_state=42)

    # Обучение модели
    model.fit(X_train_tfidf, y_train)

    print('Предсказание на тестовых данных:')
    y_pred = model.predict(X_test_tfidf)
    printRes(y_test, y_pred)

    print('Предсказание на валидирующих данных:')
    y_pred_val = model.predict(X_test_val_tfidf)
    printRes(y_test_val, y_pred_val)

    return model

def save_model_and_vectorizer(model, model_filename, vectorizer, vectorizer_filename):
    joblib.dump(model, model_filename)
    joblib.dump(vectorizer, vectorizer_filename)

def validate_saved_model(model_filename, vectorizer_filename, X_test_val, y_test_val):
    model = joblib.load(model_filename)
    vectorizer = joblib.load(vectorizer_filename)
    X_test_val_tfidf = vectorizer.transform(X_test_val)
    y_pred_val = model.predict(X_test_val_tfidf)
    printRes(y_test_val, y_pred_val)

# Загрузка данных
data = pd.read_csv('GPW/training.csv')  # Укажите путь к вашему файлу с данными

# Загрузка тестовых данных
test_data = pd.read_csv('GPW/validating.csv')  # Укажите путь к вашему файлу с тестовыми данными

# Разделение данных на признаки и целевую переменную
X = data['Query']
y = data['Target']

# Разделение данных на признаки и целевую переменную
X_test_val = test_data['Query']
y_test_val = test_data['Target']

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Векторизация данных
X_test_tfidf, X_test_val_tfidf, X_train_tfidf, vectorizer = vectorising(X_test, X_test_val, X_train)

# Сохранение векторизатора
vectorizer_filename = 'vectorizer.pkl'
joblib.dump(vectorizer, vectorizer_filename)

print("Рандомный лес:")
rf_model = randomForestModel(X_train_tfidf, y_train, X_test_tfidf, y_test, X_test_val_tfidf, y_test_val)
save_model_and_vectorizer(rf_model, 'random_forest_model.pkl', vectorizer, vectorizer_filename)

print("\nГрадиентный бустинг:")
gb_model = gradientBoostingModel(X_train_tfidf, y_train, X_test_tfidf, y_test, X_test_val_tfidf, y_test_val)
save_model_and_vectorizer(gb_model, 'gradient_boosting_model.pkl', vectorizer, vectorizer_filename)

print("\nАдаптивный бустинг:")
ab_model = adaBoostingModel(X_train_tfidf, y_train, X_test_tfidf, y_test, X_test_val_tfidf, y_test_val)
save_model_and_vectorizer(ab_model, 'ada_boosting_model.pkl', vectorizer, vectorizer_filename)

# Проверка сохраненной модели Random Forest
print("\nПроверка сохраненной модели Random Forest:")
validate_saved_model('random_forest_model.pkl', vectorizer_filename, X_test_val, y_test_val)

# Проверка сохраненной модели Gradient Boosting
print("\nПроверка сохраненной модели Gradient Boosting:")
validate_saved_model('gradient_boosting_model.pkl', vectorizer_filename, X_test_val, y_test_val)

# Проверка сохраненной модели AdaBoost
print("\nПроверка сохраненной модели AdaBoost:")
validate_saved_model('ada_boosting_model.pkl', vectorizer_filename, X_test_val, y_test_val)
