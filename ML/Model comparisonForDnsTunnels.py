import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

def printRes(y_test, y_pred):
    # Оценка модели
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print(f'Accuracy: {accuracy}')
    print('Classification Report:')
    print(report)

def randomForestModel(X_train, y_train, X_test, y_test, X_test_val, y_test_val):
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', RandomForestClassifier(n_estimators=200, max_depth=20, min_samples_split=5, random_state=42))
    ])

    # Обучение модели
    pipeline.fit(X_train, y_train)

    print('Предсказание на тестовых данных:')
    y_pred = pipeline.predict(X_test)
    printRes(y_test, y_pred)

    print('Предсказание на валидирующих данных:')
    y_pred_val = pipeline.predict(X_test_val)
    printRes(y_test_val, y_pred_val)

def gradientBoostingModel(X_train, y_train, X_test, y_test, X_test_val, y_test_val):
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', GradientBoostingClassifier(n_estimators=200, max_depth=3, min_samples_split=5, random_state=42))
    ])

    # Обучение модели
    pipeline.fit(X_train, y_train)

    print('Предсказание на тестовых данных:')
    y_pred = pipeline.predict(X_test)
    printRes(y_test, y_pred)

    print('Предсказание на валидирующих данных:')
    y_pred_val = pipeline.predict(X_test_val)
    printRes(y_test_val, y_pred_val)

def adaBoostingModel(X_train, y_train, X_test, y_test, X_test_val, y_test_val):
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
        ('clf', AdaBoostClassifier(n_estimators=200, random_state=42))
    ])

    # Обучение модели
    pipeline.fit(X_train, y_train)

    print('Предсказание на тестовых данных:')
    y_pred = pipeline.predict(X_test)
    printRes(y_test, y_pred)

    print('Предсказание на валидирующих данных:')
    y_pred_val = pipeline.predict(X_test_val)
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


print("Рандомный лес:")
randomForestModel(X_train, y_train, X_test, y_test, X_test_val, y_test_val)

print("\nГрадиентный бустинг:")
gradientBoostingModel(X_train, y_train, X_test, y_test, X_test_val, y_test_val)

print("\nАдаптивный бустинг:")
adaBoostingModel(X_train, y_train, X_test, y_test, X_test_val, y_test_val)
