import React, { useMemo, useCallback, useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend } from 'chart.js';
import ZoomPlugin from 'chartjs-plugin-zoom';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, ZoomPlugin);

// Цвета
const Utils = {
  CHART_COLORS: {
    blue: 'rgba(54, 162, 235, 1)',
    yellow: 'rgba(255, 206, 86, 1)',
    red: 'rgba(255, 99, 132, 1)'
  },
};

// Опции для графика
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
  },
  plugins: {
    zoom: {
      pan: {
        enabled: true, // Включить перемещение (pan)
        mode: 'xy', // Перемещение по обеим осям
        speed: 10, // Чувствительность перемещения
        threshold: 10 // Минимальное расстояние для начала перемещения
      },
      zoom: {
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true
        },
        mode: 'x', // Включить масштабирование по обеим осям
      }
    },
    title: {
      display: true,
      text: ['График детектирования вредоносных доменов по времени'],
      font: {
        size: 18,
      },
      color: '#4b5563',
      padding: {
        top: 2,
        bottom: 2
      }
    }
  }
};

// Компонент графика
export const TimeQuantityChart = ({ dataJson }) => {
  // Состояние для отслеживания данных
  const [chartKey, setChartKey] = useState(0);

  // Функция для создания градиента
  const getGradient = useCallback((ctx, chartArea) => {
    let width, height, gradient;
    const chartWidth = chartArea.right - chartArea.left;
    const chartHeight = chartArea.bottom - chartArea.top;
    if (!gradient || width !== chartWidth || height !== chartHeight) {
      width = chartWidth;
      height = chartHeight;
      gradient = ctx.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
      gradient.addColorStop(0, Utils.CHART_COLORS.blue);
      gradient.addColorStop(0.5, Utils.CHART_COLORS.yellow);
      gradient.addColorStop(1, Utils.CHART_COLORS.red);
    }
    return gradient;
  }, []);

  // Генерация данных для графика
  const chartData = useMemo(() => {
    const labels = Array.from({ length: 24 }, (_, i) => {
      const hour = ('0' + i).slice(-2);
      return `${hour}:00`;
    });

    const datasets = [
      {
        label: 'Кол-во угроз',
        data: [],
        fill: false,
        borderColor: function(context) {
          const chart = context.chart;
          const { ctx, chartArea } = chart;

          if (!chartArea) {
            return null;
          }
          return getGradient(ctx, chartArea);
        },
        tension: 0.1
      }
    ];

    if (dataJson && Array.isArray(dataJson['threadsByTime'])) {
      datasets[0].data = dataJson['threadsByTime'];
    }

    return { labels, datasets };
  }, [dataJson, getGradient]);

  // Обновление ключа для принудительной перерисовки компонента
  useEffect(() => {
    setChartKey(prevKey => prevKey + 1);
  }, [dataJson]);

  return (
    <div style={{ height: '300px', width: '750px' }} className="flex items-center flex-col items-start p-4 border rounded shadow-lg">
      <Line key={chartKey} data={chartData} options={options} />
    </div>
  );
};
