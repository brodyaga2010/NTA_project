import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from datetime import datetime
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS


def model_dns(validName):
    test_data = pd.read_csv(validName)
    if 'Query' not in test_data.columns:
        print("Поле 'Query' не найдено в датасете.")
        return [0]
    X_test_val = test_data['Query']

    vectorizer = joblib.load('vectorizer.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('gradient_boosting_model.pkl')
    y_pred = model.predict(X_test_val_tfidf)
    return y_pred.tolist()


def model_dga(validName):
    test_data = pd.read_csv(validName)
    if 'Query' not in test_data.columns:
        print("Поле 'Query' не найдено в датасете.")
        return [0]
    X_test_val = test_data['Query']

    vectorizer = joblib.load('model_dga_vectorizer.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('model_dga_AdaBoost.pkl')
    y_pred = model.predict(X_test_val_tfidf)
    return y_pred.tolist()


def getResPredict(predictionOfDns, predictionOfDga):
    res = [0] * len(predictionOfDns)
    for i in range(len(predictionOfDns)):
        if predictionOfDns[i] + predictionOfDga[i] > 0:
            res[i] = 1
        else:
            res[i] = 0

    return res

def getListOfThreds(filename, resPredict):
    df = pd.read_csv(filename)  # Используем пробел в качестве разделителя

    # Проверка, что длина предсказаний совпадает с количеством строк в датасете
    if len(resPredict) != len(df):
        raise ValueError("Количество предсказаний должно совпадать с количеством строк в датасете")

    # Создание списка строк с данными, для которых предсказание равно 1
    positive_predictions = []
    for index, row in df.iterrows():
        if resPredict[index] == 1:
            row_string = f"{row['Query']} {row['Time']}"
            positive_predictions.append(row_string)

    return positive_predictions

def getThreadsByTime(filename, predictionOfDns, predictionOfDga):
    data = pd.read_csv(filename)
    if 'Time' not in data.columns:
        print("Поле 'Time' не найдено в датасете.")
        return [0] * 24
    res = [0] * 24
    # Извлечение часа из поля 'Time'
    data['Hour'] = data['Time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').hour)

    # Цикл для вывода всех часов
    for index, row in data.iterrows():
        if predictionOfDns[index] > 0:
            res[int(row['Hour'])] += 1
        if predictionOfDga[index] > 0:
            res[int(row['Hour'])] += 1

    return res

def getRes(filename, dnsPred, dgaPred):
    resPredict = getResPredict(dnsPred, dgaPred)
    dnsThreadCount = dnsPred.count(1)
    dgaThreadCount = dgaPred.count(1)
    threadsByTIme = getThreadsByTime(filename, dnsPred, dgaPred)

    res = {
        "dnsThreadCount": dnsThreadCount, # Количество DNS тунелей
        "dgaThreadCount": dgaThreadCount, # Количество DGA атак
        "threadsByTIme": threadsByTIme, # количество угроз по часам
        "listOfThreads": getListOfThreds(filename, resPredict) # Список для результирующей штуки
    }
    return res

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/upload": {"origins": "http://172.25.67.192:3005"}})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        print('Нет файла в запросе')
        return 'Нет файла в запросе', 400
    file = request.files['file']
    if file.filename == '':
        print('Нет выбранного файла')
        return 'Нет выбранного файла', 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join('.', filename))
        print(f'Сохранен файл {filename}')

        response = app.make_response('Файл успешно загружен')
        response.headers['Access-Control-Allow-Origin'] = 'http://172.25.67.192:3005'
        response.headers['Access-Control-Allow-Credentials'] = 'true'

        dnsPred = model_dns(filename)
        dgaPred = model_dga(filename)
        res = getRes(filename, dnsPred, dgaPred)

        if os.path.exists(filename):
            os.remove(filename)
            print(f'Удален файл {filename}')

        return jsonify(res), 200

if __name__ == '__main__':
    port = 5000
    app.run(host='172.25.114.105', debug=True, port=port)
