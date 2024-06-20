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
      <div className="bg-gray-800 text-white p-2">
        <h1 className="m-0">RX-NTA</h1>
      </div>
      <div className="mt-2 bg-gray-800 h-1"></div>
      
      <div className="flex justify-between pb-4">
        <div className="w-1/2">
          <UploadFile onUploadSuccess={handleUploadSuccess}/>
        </div>
        <div className="flex"> 
          {/*<HorizontalBarChart />*/}
          <ListThreads dataJson={uploadedData}/>
          <CountTunels dataJson={uploadedData}/>
        </div>
      </div>
      <TimeQuantityChart dataJson={uploadedData}/>


    </div>
  );
}

export default App;
