import React, { useState } from 'react';

export const ListThreads = ({ dataJson }) => {

    const containerStyle = {
        width: '800px',
        maxHeight: '400px', // Ограничение по высоте
        overflowY: 'auto', // Полоса прокрутки по вертикали
    };

    if (dataJson && typeof dataJson === 'object' && 'listOfThreads' in dataJson) {
        const data = dataJson['listOfThreads'];


        return (
            <div className='mr-4'>
                <h2 className="text-xl font-semibold mb-0 border-b-2 border-gray-300 pb-2 text-blue-600 bg-white shadow-lg p-4">Список угроз</h2>
                <div style={containerStyle} className="bg-white rounded-lg shadow-lg p-4">
                    <ul className="divide-y divide-gray-300">
                        {data.map((str, index) => {
                            const [Name, Date, Time] = str.split(' ');
                            return (
                                <li key={index} className="py-2">
                                    <span className="text-red-600">{Name}</span>
                                    <br />
                                    <span className="text-blue-600">{Date} {Time}</span>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            </div>
        );
    } 
    else
    {
        return (
            <div className='mr-4'>
                <h2 className="text-xl font-semibold mb-0 border-b-2 border-gray-300 pb-2 text-blue-600 bg-white shadow-lg p-4">Список угроз</h2>
                <div style={containerStyle} className="bg-white rounded-lg shadow-lg p-4 text-center">
                    No data available
                </div>
            </div>
        );
    }
};
