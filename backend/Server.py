import pandas as pd
import joblib
from datetime import datetime
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from collections import Counter
import time

def model_dns(test_data):
    X_test_val = test_data['Query']

    vectorizer = joblib.load('vectorizer.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('gradient_boosting_model.pkl')
    y_pred = model.predict(X_test_val_tfidf)
    return y_pred.tolist()


def model_dga(test_data):
    X_test_val = test_data['Query']

    vectorizer = joblib.load('tfidf_vectorizer_xtrain.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('dga_model_rf.pkl')
    y_pred = model.predict(X_test_val_tfidf)
    return y_pred.tolist()


def model_dga_subclass(test_data):
    X_test_val = test_data['Query']

    vectorizer = joblib.load('vectorizer_gram2-5.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('dga_subclass_logres.pkl')
    y_pred = model.predict(X_test_val_tfidf)

    label_encoder = joblib.load('label_encoder.pkl')
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    prediction_counts = Counter(y_pred_labels)

    labels = list(prediction_counts.keys())
    counts = list(prediction_counts.values())

    return {"labels_subclass": labels, "counts_subclass": counts}


def getResPredict(predictionOfDns, predictionOfDga):
    res = [0] * len(predictionOfDns)
    for i in range(len(predictionOfDns)):
        if predictionOfDns[i] + predictionOfDga[i] > 0:
            res[i] = 1
        else:
            res[i] = 0

    return res

def getListOfThreads(data, resPredict):
    # Проверка, что длина предсказаний совпадает с количеством строк в датасете
    if len(resPredict) != len(data):
        raise ValueError("Количество предсказаний должно совпадать с количеством строк в датасете")

    # Создание списка строк с данными, для которых предсказание равно 1
    positive_predictions = []
    for index, row in data.iterrows():
        if resPredict[index] == 1:
            query = row['Query']
            if (len(query.split(' ')) == 1):
                row_string = f"{row['Query']} {row['Time']}"
            else:
                row_string = f"{query.split(' ')[1]} {row['Time']}"
            #row_string = f"{row['Query']} {row['Time']}"
            positive_predictions.append(row_string)

    return positive_predictions

def getThreadsByTime(data, predictionOfDns, predictionOfDga):
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

def getRes(data, dnsPred, dgaPred):
    resPredict = getResPredict(dnsPred, dgaPred)
    dnsThreadCount = dnsPred.count(1)
    dgaThreadCount = dgaPred.count(1)
    threadsByTime = getThreadsByTime(data, dnsPred, dgaPred)
    dgaSubclassCounts = model_dga_subclass(data)  # Получаем предсказания DGA_subclass

    res = {
        "totalPackagesCount": len(resPredict),
        "totalThreadsCount": resPredict.count(1),
        "dnsThreadCount": dnsThreadCount,  # Количество DNS тунелей
        "dgaThreadCount": dgaThreadCount,  # Количество DGA атак
        "threadsByTime": threadsByTime,  # количество угроз по часам
        "listOfThreads": getListOfThreads(data, resPredict),
        "labels_subclass": dgaSubclassCounts["labels_subclass"],
        "labels_count_subclass": dgaSubclassCounts["counts_subclass"]
    }

    return res


def validate_dataset(data):
    # Проверка наличия обязательных столбцов
    required_columns = {'Query', 'Time'}
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        print(f"Отсутствуют обязательные столбцы: {', '.join(missing_columns)}")
        return False

    # Проверка одинакового числа строк в каждом столбце
    column_lengths = data.apply(lambda col: col.notna().sum())
    unique_lengths = column_lengths.unique()
    if len(unique_lengths) > 1:
        print("В столбцах разное количество непустых строк:")
        print(column_lengths)
        return False

    print("Датасет прошел проверку.")
    return True

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
        start_time = time.time()

        filename = secure_filename(file.filename)
        file.save(os.path.join('.', filename))
        print(f'Сохранен файл {filename}')

        response = app.make_response('Файл успешно загружен')
        response.headers['Access-Control-Allow-Origin'] = 'http://172.25.67.192:3005'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        data = pd.read_csv(filename)
        if validate_dataset(data) == False:
            return 'Некорректный датасет', 517

        dnsPred = model_dns(data)
        dgaPred = model_dga(data)
        res = getRes(data, dnsPred, dgaPred)

        if os.path.exists(filename):
            os.remove(filename)
            print(f'Удален файл {filename}')

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Время выполнения: {elapsed_time:.6f} секунд")

        return jsonify(res), 200

if __name__ == '__main__':
    port = 5000
    app.run(host='172.25.114.105', debug=True, port=port)
