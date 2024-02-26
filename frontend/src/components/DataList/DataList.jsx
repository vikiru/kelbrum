import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const DataList = ({ title, data, path }) => {
    const navigate = useNavigate();

    const sortEntries = (a, b) => {
        const aKey = a[1].key;
        const bKey = b[1].key;
        if (aKey === 'unknown') return 1;
        if (bKey === 'unknown') return -1;
        return aKey.localeCompare(bKey);
    };

    return (
        <div className="bg-secondary">
            <h2 className="bg-secondary bg-opacity-50 py-4 text-center text-2xl font-bold text-primary underline">
                {title}
            </h2>
            <div className="mt-4 flex flex-wrap justify-center gap-4">
                {Object.entries(data)
                    .sort(sortEntries)
                    .map(([key, value], index) => (
                        <Link
                            key={key}
                            to={`/anime/${path}/${index + 1}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="card w-full cursor-pointer rounded-lg bg-primary text-primary-content shadow-lg transition-shadow duration-300 hover:bg-opacity-75 hover:shadow-xl xs:w-1/2 md:w-1/3 lg:w-1/4"
                        >
                            <div className="card-body flex items-center justify-center p-4">
                                <h2 className="card-title text-center text-lg font-semibold text-secondary">
                                    {value.key} ({value.values.length})
                                </h2>
                            </div>
                        </Link>
                    ))}
            </div>
        </div>
    );
};

export default DataList;
