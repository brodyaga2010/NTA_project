import React, { useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

// Регистрация шкал и элементов графика только для этого компонента
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Функция для определения цвета в зависимости от значения
const determineBackgroundColor = (context) => {
  const value = context.dataset.data[context.dataIndex];
  if (value > 5000) {
    return 'rgba(255, 99, 132, 0.9)'; // Красный цвет
  } else if (value > 2000) {
    return 'rgba(54, 162, 235, 0.9)'; // Синий цвет
  } else {
    return 'rgba(75, 192, 192, 0.9)'; // Зеленый цвет
  }
};

export const ClassHorizontalBarChart = ({ dataJson }) => {
  // Генерация данных для графика и опций
  const { data, options } = useMemo(() => {
    const data = {
      labels: ['-', '-', '-', 'No data available', '-', '-', '-'],
      datasets: [
        {
          label: '',
          data: [],
          backgroundColor: [],
          barThickness: 27, // Толщина столбцов
        }
      ]
    };

    if (dataJson && Array.isArray(dataJson['labels_count_subclass'])) {
      data.datasets[0].data = dataJson['labels_count_subclass'];
      data.labels = dataJson['labels_subclass'];
    }

    const maxValue = Math.max(...data.datasets[0].data);

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
          },
          max: maxValue * 1.5 // Установка максимального значения для оси X
        },
        y: {
          display: true,
          grid: {
            display: false,
          },
          ticks: {
            display: true,
            drawBorder: false,
            font: {
              size: 14, // Размер шрифта меток оси Y
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false,
        },
        title: {
          display: true, // Включает отображение заголовка
          text: ['Распределение вредоносных', 'доменов на подклассы '], // Текст заголовка
          font: {
            size: 16, // Размер шрифта заголовка
            weight: 'bold' // Жирный шрифт заголовка
          },
          color: '#4b5563',
          padding: {
            top: 2,
            bottom: 5
          }
        },
        datalabels: {
          anchor: 'end',
          align: 'end',
          color: 'black',
          font: {
            weight: 'bold'
          },
        }
      }
    };

    // Заполнение массива backgroundColor на основе данных
    data.datasets[0].backgroundColor = data.datasets[0].data.map((value, index) => determineBackgroundColor({ dataset: { data: data.datasets[0].data }, dataIndex: index }));

    return { data, options };
  }, [dataJson]);

  return (
    <div style={{ height: '300px', width: '400px' }} className="flex items-center flex-col items-start p-4 border rounded shadow-lg">
      <Bar data={data} options={options} plugins={[ChartDataLabels]} />
    </div>
  );
};
