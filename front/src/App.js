import { UploadFile } from "./components/UploadFile";
import { CountTunels } from "./components/CountTunels";
import { TimeQuantityChart } from "./components/TimeQuantityChart";
import { HorizontalBarChart } from "./components/HorizontalBarChart";
import { ListThreads } from "./components/ListThreads";
import React, { useEffect, useState } from 'react';

function App() {
  const [uploadedData, setUploadedData] = useState(null);

  useEffect(() => {
    document.title = 'RX-NTA';
  }, []);

  const handleUploadSuccess = (data) => {
    setUploadedData(data);
  };

  return (
    <div className="App">
      {/* Шапка приложения */}
      <div className="bg-gray-800 text-white p-2">
        <h1 className="m-0">RX-NTA</h1>
      </div>
      <div className="mt-2 bg-gray-800 h-1"></div>

      <div className="flex flex-wrap justify-center sm:justify-start gap-4">
        <div className="m-2 flex-shrink-0">
          <UploadFile onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Компоненты рендерятся только если данные загружены */}
        {uploadedData && (
          <>
            <div className="m-2 flex-shrink-0">
              <ListThreads dataJson={uploadedData} className="w-full" />
            </div>
            <div className="m-2 flex-shrink-0">
              <CountTunels dataJson={uploadedData} className="h-full" />
            </div>
            <div className="m-2 flex-shrink-0">
              <HorizontalBarChart dataJson={uploadedData} />
            </div>
            <div className="m-2 flex-shrink-0">
              <TimeQuantityChart dataJson={uploadedData} className="w-full" />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
