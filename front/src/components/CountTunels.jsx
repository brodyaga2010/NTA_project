import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

  const options = {
    maintainAspectRatio: false,
    aspectRatio: 1, // Уменьшите это значение, чтобы сделать диаграмму меньше
    plugins: {
      legend: 
      {
        display: false
      },
    }
  };

export const CountTunels = ({ dataJson }) => {

    const data = {
      labels: ['DNS-туннелей', 'Семейство DGA'],
      datasets: [
        {
          data: [0, 0],
          backgroundColor: ['#FF6384', '#36A2EB'],
          hoverBackgroundColor: ['#FF6384', '#36A2EB'],
        },
      ],
    };


    if (dataJson && typeof dataJson === 'object' && 'dnsThreadCount' in dataJson && 'dgaThreadCount' in dataJson) {
      data.datasets[0].data = [dataJson['dnsThreadCount'], dataJson['dgaThreadCount']];
    }

    const total = data.datasets[0].data.reduce((sum, value) => sum + value, 0);
    console.log(total);


    const centerTextPlugin = {
        id: 'centerText',
        beforeDraw: (chart) => {
          const ctx = chart.ctx;
          const width = chart.width;
          const height = chart.height;
          ctx.save();
          
          const fontSize = (height / 160).toFixed(2); // Можете изменить значение для установки размера шрифта
          ctx.font = fontSize + "em sans-serif";
          ctx.textBaseline = "middle";
          ctx.textAlign = "center";
      
          // Разделите текст на строки
          const lines = [`Итог: ${total}`];
          const textX = width / 2;
          const textY = height / 2 - (lines.length - 1) * fontSize * 8;
      
          // Отобразите каждую строку отдельно
          lines.forEach((line, index) => {
            ctx.fillText(line, textX, textY + index * fontSize * 16);
          });
      
          ctx.restore();
        }
      };

    return (
        <div style={{ width: '250px' }} className="flex items-center flex-col items-start max-w-md p-4 border rounded shadow-lg">
           {dataJson ? (
                <div style={{ width: '200px', height: '200px' }}>
                    <Doughnut data={data} options={options} plugins={[centerTextPlugin]} />
                </div>
            ) : (
                <p>No data available</p>
            )}

            {/* Легенда */}
            <div className="flex flex-col items-start pl-4 mt-4 w-full">
                {data.labels.map((label, index) => (
                    <div key={label} className="flex items-center mb-2">
                        <span className="flex-shrink-0 w-9 h-9 rounded-full mr-2" style={{ backgroundColor: data.datasets[0].backgroundColor[index] }}></span>
                        <div className="flex flex-col items-center w-full pl-2">
                            <span className="w-full text-center">{data.datasets[0].data[index]}</span>
                            <div className="h-px bg-black w-32 my-1"></div>
                            <span>{label}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>)
};