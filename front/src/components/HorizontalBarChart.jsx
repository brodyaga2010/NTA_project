import React from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const data = {
    labels: ['Label 1', 'Label 2', 'Label 3', 'Label 4' , 'Label 5', 'Label 6'],
    datasets: [
      {
        label: '',
        data: [10, 20, 30, 25, 5, 19],
        backgroundColor: function(context) {
          const value = context.dataset.data[context.dataIndex];
          if (value < 15) {
            return 'rgba(255, 99, 132, 0.5)'; // red
          } else if (value < 25) {
            return 'rgba(54, 162, 235, 0.5)'; // blue
          } else {
            return 'rgba(75, 192, 192, 0.5)'; // green
          }
        },
      }
    ]
  };

  const options = {
    maintainAspectRatio: false,
    indexAxis: 'y',
    scales: {
      x: {
        display: false,
        grid: {
          display: false,
        },
        ticks: {
          display: false,
        }
      },
      y: {
        display: true, // Включает ось Y
        grid: {
          display: false, // Отключает сетку по оси Y
        },
        ticks: {
          display: true, // Отображает метки по оси Y
          drawBorder: false, // Отключает линию границы оси Y
        }
      }
    },
    plugins: {
      legend: {
        display: false,
      }
    }
  };
  

export const HorizontalBarChart = () => {
    return (
        <div style={{ height: '300px', width: '300px' }} className="flex items-center flex-col items-start p-4 border rounded shadow-lg">
            <Bar data={data} options={options} />
        </div>
    );
};
