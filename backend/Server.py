import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from datetime import datetime
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS


def model(validName):
    data = pd.read_csv('GPW/training.csv')
    test_data = pd.read_csv(validName)
    X = data['Query']
    X_test_val = test_data['Query']

    vectorizer = joblib.load('vectorizer.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('gradient_boosting_model.pkl')
    y_pred = model.predict(X_test_val_tfidf)
    print(y_pred)
    return y_pred.tolist()


def getResPredict(predictionOfDns, predictionOfDga):
    res = [0] * len(predictionOfDns)
    for i in range(len(predictionOfDns)):
        if predictionOfDns[i] + predictionOfDga[i] > 0:
            res[i] = 1
        else:
            res[i] = 0

    return res

def getThreadsByTime(filename, predictionOfDns, predictionOfDga):
    data = pd.read_csv(filename)
    print(data.head(10))
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

def getRes(filename, dnsPred):
    dgaPred = [0] * len(dnsPred)  # Место для второй модели
    resPredict = getResPredict(dnsPred, dgaPred)
    dnsThreadCount = dnsPred.count(1)
    dgaThreadCount = dgaPred.count(1)
    threadsByTIme = getThreadsByTime(filename, dnsPred, dgaPred)

    res = {
        "dnsThreadCount": dnsThreadCount, # Количество DNS тунелей
        "dgaThreadCount": dgaThreadCount, # Количество DGA атак
        "threadsByTIme": threadsByTIme, # количество угроз по часам
        "listOfThreads": resPredict # Список для результирующей штуки
    }
    return res

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://ipAdressOfwebSite:posrt"}})

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
        print('Сохранен файл ' + filename)

        response = app.make_response('Файл успешно загружен')
        response.headers['Access-Control-Allow-Origin'] = 'http://ipAdressOfwebSite:port'
        response.headers['Access-Control-Allow-Credentials'] = 'true'

        dnsPred = model(filename)
        res = getRes(filename, dnsPred)

        if os.path.exists(filename):
            os.remove(filename)
            print(f'{filename} был удален')

        return jsonify(res), 200

if __name__ == '__main__':
    port = 5328
    app.run(host='host', debug=True, port=port)
