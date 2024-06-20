import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        ticks: {
          autoSkip: true,
          maxTicksLimit: 24
        },
        title: {
            display: true,
            text: 'Время' // Подпись оси X
          }
      },
      y: {
        beginAtZero: true,        
      }
    }
  };
  

export const TimeQuantityChart = ({ dataJson }) => {
  const data = {
    labels: Array.from({ length: 24 }, (_, i) => i.toString()), // Метки времени
    datasets: [
      {
        label: 'Кол-во угроз',
        data:[ ], // Данные количества
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  if (dataJson && typeof dataJson === 'object' && 'threadsByTIme' in dataJson) {
    data.datasets[0].data = dataJson['threadsByTIme'];
  }


    return (
        <div style={{ height: '300px' }} className="flex items-center flex-col items-start p-4 border rounded shadow-lg">
            <Line data={data} options={options} />
        </div>
    );
};
