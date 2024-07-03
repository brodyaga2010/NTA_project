import pandas as pd
import joblib
from datetime import datetime
from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from collections import Counter
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import numpy as np

def model_dns(test_data):
    X_test_val = test_data['Query']

    vectorizer = joblib.load('vectorizer.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('random_forest_model.pkl')
    model.set_params(n_jobs=-1)

    y_pred = model.predict(X_test_val_tfidf)
    return y_pred.tolist()


def model_dga(test_data):
    X_test_val = test_data['Query']

    vectorizer = joblib.load('tfidf_vectorizer_xtrain.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('dga_model_rf.pkl')
    model.set_params(n_jobs=-1)

    y_pred = model.predict(X_test_val_tfidf)
    return y_pred.tolist()


def model_dga_subclass(test_data):
    X_test_val = test_data['Query']

    vectorizer = joblib.load('vectorizer_gram2-5.pkl')
    X_test_val_tfidf = vectorizer.transform(X_test_val)

    model = joblib.load('dga_subclass_logres.pkl')
    model.set_params(n_jobs=-1)
    y_pred = model.predict(X_test_val_tfidf)

    label_encoder = joblib.load('label_encoder.pkl')
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    prediction_counts = Counter(y_pred_labels)

    labels = list(prediction_counts.keys())
    counts = list(prediction_counts.values())

    return {"labels_subclass": labels, "counts_subclass": counts}


def process_data_in_threats_by_models(data):
    dns = []
    dga = []
    dga_sub = []
    with ThreadPoolExecutor(max_workers=None) as executor:
        future = executor.submit(model_dns, data)
        dns = future.result()

        future = executor.submit(model_dga, data)
        dga = future.result()

        future = executor.submit(model_dga_subclass, data)
        dga_sub = future.result()

    return dns, dga, dga_sub


def process_data_in_threads_by_data(data):
    # Делим DataFrame на три части
    data_split = np.array_split(data, 3)
    dns_split = [[], [], []]
    dga_split = [[], [], []]
    dga_sub_split = [{}, {}, {}]

    with ProcessPoolExecutor(max_workers=None) as executor:
        futures = {}

        # Создаем задачи для каждой части данных и каждой модели
        for i in range(3):
            futures[executor.submit(model_dns, data_split[i])] = ('dns', i)
            futures[executor.submit(model_dga, data_split[i])] = ('dga', i)
            futures[executor.submit(model_dga_subclass, data_split[i])] = ('dga_sub', i)

        # Обрабатываем результаты по мере их готовности
        for future in as_completed(futures):
            model_type, index = futures[future]
            result = future.result()
            if model_type == 'dns':
                dns_split[index] = result
            elif model_type == 'dga':
                dga_split[index] = result
            elif model_type == 'dga_sub':
                dga_sub_split[index] = result

    # Объединяем результаты
    dns_res = dns_split[0] + dns_split[1] + dns_split[2]
    dga_res = dga_split[0] + dga_split[1] + dga_split[2]
    dga_sub_res = {}
    for d in dga_sub_split:
        dga_sub_res.update(d)

    return dns_res, dga_res, dga_sub_res


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


def get_res_predict(prediction_of_dns, prediction_of_dga):
    res = [0] * len(prediction_of_dns)
    for i in range(len(prediction_of_dns)):
        if prediction_of_dns[i] + prediction_of_dga[i] > 0:
            res[i] = 1
        else:
            res[i] = 0
    return res


def get_list_of_threats(data, res_predict):
    # Проверка, что длина предсказаний совпадает с количеством строк в датасете
    if len(res_predict) != len(data):
        raise ValueError("Количество предсказаний должно совпадать с количеством строк в датасете")

    # Создание списка строк с данными, для которых предсказание равно 1
    positive_predictions = []
    for index, row in data.iterrows():
        if res_predict[index] == 1:
            query = row['Query']
            if (len(query.split(' ')) == 1):
                row_string = f"{row['Query']} {row['Time']}"
            else:
                row_string = f"{query.split(' ')[1]} {row['Time']}"
            positive_predictions.append(row_string)

    return positive_predictions


def get_threats_by_time(data, prediction_of_dns, prediction_of_dga):
    if 'Time' not in data.columns:
        print("Поле 'Time' не найдено в датасете.")
        return [0] * 24
    res = [0] * 24
    # Извлечение часа из поля 'Time'
    data['Hour'] = data['Time'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').hour)

    # Цикл для вывода всех часов
    for index, row in data.iterrows():
        if prediction_of_dns[index] > 0:
            res[int(row['Hour'])] += 1
        if prediction_of_dga[index] > 0:
            res[int(row['Hour'])] += 1

    return res


def get_res(data, dns_pred, dga_pred, dga_subclass_counts):
    res_predict = get_res_predict(dns_pred, dga_pred)
    dns_threat_count = dns_pred.count(1)
    dga_threat_count = dga_pred.count(1)
    threats_by_time = get_threats_by_time(data, dns_pred, dga_pred)

    res = {
        "totalPackagesCount": len(res_predict),
        "totalThreadsCount": res_predict.count(1),
        "dnsThreadCount": dns_threat_count,  # Количество DNS тунелей
        "dgaThreadCount": dga_threat_count,  # Количество DGA атак
        "threadsByTime": threats_by_time,  # количество угроз по часам
        "listOfThreads": get_list_of_threats(data, res_predict),
        "labels_subclass": dga_subclass_counts["labels_subclass"],
        "labels_count_subclass": dga_subclass_counts["counts_subclass"]
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
        start_time = time.time()

        filename = secure_filename(file.filename)
        if filename.split('.')[1] != 'csv':
            print('Некорректный формат файла')
            return 'Некорректный формат файла', 450

        file.save(os.path.join('.', filename))
        print(f'Сохранен файл {filename}')

        response = app.make_response('Файл успешно загружен')
        response.headers['Access-Control-Allow-Origin'] = 'http://172.25.67.192:3005'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        data = pd.read_csv(filename)
        if validate_dataset(data) == False:
            return 'Некорректный датасет', 517

        #dnsPred = model_dns(data)
        #dgaPred = model_dga(data)
        #dgaSubclassCounts = model_dga_subclass(data)

        dns_pred, dga_pred, dga_subclass_counts = process_data_in_threads_by_data(data)
        res = get_res(data, dns_pred, dga_pred, dga_subclass_counts)

        if os.path.exists(filename):
            os.remove(filename)
            print(f'Удален файл {filename}')

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Время выполнения: {elapsed_time:.6f} секунд")

        return jsonify(res), 200

if __name__ == '__main__':
    port = 5000
    host = '172.25.114.105'
    app.run(host=host, debug=True, port=port)
