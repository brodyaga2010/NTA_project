import { useState, useRef } from "react";

const hostUrl = 'http://localhost:5000/upload';

export const UploadFile = () =>
{
    const filePicker = useRef(null);
    const [selectedFile, setSelctedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('idle'); // 'uploading', 'failed', 'uploaded'

    const handleChange = (event) => {
        console.log(event.target.files);
        const file = event.target.files[0];
        setSelctedFile(file);
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
                body: formData,
            });
            
            if (res.ok) {
                setUploadStatus('uploaded');
            } else {
                setUploadStatus('failed');
            }
        } catch (error) {
            setUploadStatus('failed');
        }
    };
    
    const handlePick = () => {
        filePicker.current.click();
    };

    return(
        <>
            <input
                className="hidden"
                type="file"
                ref={filePicker}
                onChange={handleChange}
                accept=".csv"
            />
    
    <div style={{ width: '250px' }} className="flex items-center flex-col items-start max-w-md p-4 border rounded shadow-lg">
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
                    uploadStatus === 'failed' ? 'text-red-500' :
                    uploadStatus === 'uploaded' ? 'text-green-500' : '-'
                }`}>
                    {uploadStatus === 'uploading' ? 'Файл загружается...' :
                    uploadStatus === 'failed' ? 'Не удалось загрузить файл' :
                    uploadStatus === 'uploaded' ? 'Файл загружен' : '-'}
                </span>
            </li>

        </ul>
    </div>
    </div>


        </>
    )
}