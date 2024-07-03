import { useState, useRef } from "react";

const hostUrl = 'http://172.25.114.105:5000/upload'; // Адрес сервера

export const UploadFile = ({ onUploadSuccess }) => {
    const filePicker = useRef(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('idle'); // 'idle', 'uploading', 'failed', 'uploaded'

    const handleChange = (event) => {
        const file = event.target.files[0];
        setSelectedFile(file);
        setUploadStatus('idle'); // Сбрасываем статус при выборе нового файла
        if (file) {
            handleUpload(file);
        }
    };

    const handleUpload = async (file) => {
        setUploadStatus('uploading');
        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch(hostUrl, {
                method: 'POST',
                credentials: 'include',
                body: formData,
            });

            if (res.ok) {
                const data = await res.json();
                setUploadStatus('uploaded');
                onUploadSuccess(data);
            } else {
                if (res.status === 517) {
                    setUploadStatus('errorFile');
                } else {
                    setUploadStatus('failed');
                }
            }
        } catch (error) {
            setUploadStatus('failed');
        }
    };

    const handleRetryUpload = () => {
        handleUpload(selectedFile);
    };

    const handlePick = () => {
        filePicker.current.click();
    };

    return (
        <>
            <input
                className="hidden"
                type="file"
                ref={filePicker}
                onChange={handleChange}
                accept=".csv"
            />

            <div style={{ width: '250px', height: '300px' }} className="flex items-center flex-col items-start max-w-md p-4 border rounded shadow-lg">
                <button
                    onClick={handlePick}
                    className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded mt-2"
                >
                    Загрузить файл
                </button>
                <br />

                <div>
                    <p className="text-lg font-semibold">Информация о файле:</p>
                    <ul className="list-disc pl-5">
                        <li><span className="font-medium">Имя:</span> {selectedFile ? selectedFile.name : '-'}</li>
                        <li><span className="font-medium">Размер:</span> {selectedFile ? `${selectedFile.size} bytes` : '-'}</li>
                        <li className="font-medium">
                            Статус: <span className={`${
                                uploadStatus === 'uploading' ? 'text-yellow-500' :
                                    uploadStatus === 'failed' || uploadStatus === 'errorFile' ? 'text-red-500' :
                                        uploadStatus === 'uploaded' ? 'text-green-500' : '-'
                                }`}>
                                {uploadStatus === 'uploading' ? 'Файл загружается...' :
                                    uploadStatus === 'failed' ? 'Не удалось загрузить файл' :
                                        uploadStatus === 'errorFile' ? 'Файл содержит некорректные данные' :
                                            uploadStatus === 'uploaded' ? 'Файл загружен' : '-'}
                            </span>
                            {uploadStatus === 'failed' && (
                                <button
                                    onClick={handleRetryUpload}
                                    className="ml-2 text-blue-500 hover:underline focus:outline-none"
                                >
                                    Попробовать ещё раз
                                </button>
                            )}
                        </li>
                    </ul>
                </div>
            </div>
        </>
    )
};
