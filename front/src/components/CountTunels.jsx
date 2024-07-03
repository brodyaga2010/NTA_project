import React, { useState, useEffect, useMemo } from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

// Опции для диаграммы
const options = {
    maintainAspectRatio: false,
    aspectRatio: 1, // Размер диаграммы
    plugins: {
        legend: {
            display: false
        },
    }
};

// Утилита для проверки и получения данных
const getChartData = (dataJson) => {
    if (dataJson && typeof dataJson === 'object' && 'dnsThreadCount' in dataJson && 'dgaThreadCount' in dataJson) {
        return {
            labels: ['DNS-туннелей', 'Семейство DGA'],
            datasets: [
                {
                    data: [dataJson['dnsThreadCount'], dataJson['dgaThreadCount']],
                    backgroundColor: ['#FF6384', '#36A2EB'],
                    hoverBackgroundColor: ['#FF6384', '#36A2EB'],
                },
            ],
        };
    }
    return null;
};

// Компонент диаграммы
export const CountTunels = ({ dataJson }) => {
    const [key, setKey] = useState(0); // Добавляем key для принудительного перерендеринга компонента

    useEffect(() => {
        // Увеличиваем key, чтобы заставить компонент перерисоваться при изменении dataJson
        setKey(prevKey => prevKey + 1);
    }, [dataJson]); // Перерендеринг компонента при изменении dataJson

    const chartData = useMemo(() => getChartData(dataJson), [dataJson]);

    // Плагин для отображения центрального текста
    const centerTextPlugin = useMemo(() => ({
        id: 'centerText',
        beforeDraw: (chart) => {
            const ctx = chart.ctx;
            const width = chart.width;
            const height = chart.height;
            ctx.save();

            const totalText = `Итог: ${dataJson ? dataJson.totalThreadsCount : 0}`;
            const fontSize = Math.min(height / 160, width / (totalText.length * 16)); // Пропорциональное уменьшение размера шрифта
            ctx.font = fontSize + "em sans-serif";
            ctx.textBaseline = "middle";
            ctx.textAlign = "center";

            // Отображение текста
            ctx.fillText(totalText, width / 2, height / 2);

            ctx.restore();
        }
    }), [dataJson]);

    return (
        <div key={key} style={{ width: '250px'}} className="flex items-center flex-col items-start max-w-md p-4 border rounded shadow-lg">
            <div style={{ marginBottom: '10px', fontSize: '18px', fontWeight: 'bold', textAlign: 'center' }} className='text-gray-600'>Виды детектируемых угроз</div>
            {chartData ? (
                <div style={{ width: '200px', height: '200px' }}>
                    <Doughnut data={chartData} options={options} plugins={[centerTextPlugin]} />
                </div>
            ) : (
                <p>No data available</p>
            )}

            {/* Легенда */}
            <div className="flex flex-col items-start pl-4 mt-4 w-full">
                {chartData && chartData.labels.map((label, index) => (
                    <div key={label} className="flex items-center mb-2">
                        <span className="flex-shrink-0 w-9 h-9 rounded-full mr-2" style={{ backgroundColor: chartData.datasets[0].backgroundColor[index] }}></span>
                        <div className="flex flex-col items-center w-full pl-2">
                            <span className="w-full text-center">{chartData.datasets[0].data[index]}</span>
                            <div className="h-px bg-black w-32 my-1"></div>
                            <span>{label}</span>
                        </div>
                    </div>
                ))}
            </div>
            <div className='pt-4'>Проверено доменов:</div>
            <>{dataJson ? dataJson.totalPackagesCount : 0}</>
        </div>
    );
};
