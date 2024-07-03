import React, { memo } from'react';
import { FixedSizeList as List } from'react-window';

// Компонент ThreadItem отображает отдельный элемент списка
const ThreadItem = memo(({ index, style, data }) => {
  const item = data[index];
  const [Name, Date, Time] = item.split(' ');

  return (
    <div className="py-2">
      <div className="pb-2 border-b border-gray-300" style={style}>
        <span className="block text-red-600 text-base">{Name}</span>
        <span className="block text-blue-600 text-base">{Date} {Time}</span>
      </div>
    </div>
  );
});

const ListThreads = memo(({ dataJson }) => {
  const data = dataJson?.listOfThreads; // Получаем данные списка из объекта dataJson

  return (
    <div className="mr-4">
      <h2 className="text-xl font-semibold mb-0 border-b-2 border pb-2 text-blue-600 bg-white shadow-lg p-4">
        Результат работы моделей по детектированию угроз
      </h2>
      {data? (
        <div className="text-xl font-semibold mb-0 border-b-2 border pb-2 pl-2 pr-2 text-blue-600 bg-white shadow-lg">
            <List
            height={400} // Высота списка
            itemCount={data.length} // Количество элементов в списке
            itemSize={50} // Высота каждого элемента списка
            width={600} // Ширина списка
            itemData={data} // Данные элементов списка
            >
            {ThreadItem}
            </List>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-lg p-4 text-center border">
          Данные отсутствуют
        </div>
      )}
    </div>
  );
});

export default ListThreads;

           