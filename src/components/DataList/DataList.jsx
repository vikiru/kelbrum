import React, { useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import DataCard from '../DataCard/DataCard';

const DataList = ({ title, data, path, customSort, capitalizeTitle = false }) => {
    const sortFunction = useMemo(() => {
        return (
            customSort ||
            ((a, b) => {
                const aKey = a.key;
                const bKey = b.key;
                if (aKey === 'Unknown') return 1;
                if (bKey === 'Unknown') return -1;
                return aKey.localeCompare(bKey);
            })
        );
    }, [customSort]);

    const sortedData = useMemo(() => {
        return [...data].sort(sortFunction);
    }, [data, sortFunction]);

    return (
        <div className="bg-secondary dark:bg-gray-900">
            <h2
                className={`bg-secondary bg-opacity-50 pb-2 pt-4 text-center  xs:text-lg  text-xl font-bold text-primary underline lg:text-4xl dark:bg-gray-900`}
            >
                {title}
            </h2>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
                {sortedData.map((item, index) => (
                    <DataCard
                        key={index}
                        path={path}
                        index={data.indexOf(item)}
                        value={item}
                        capitalizeTitle={capitalizeTitle}
                    />
                ))}
            </div>
        </div>
    );
};

export default DataList;
