import React, { useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const DataList = ({ title, data, path, customSort, capitalizeTitle = false }) => {
    const sortFunction = useMemo(() => {
        return (
            customSort ||
            ((a, b) => {
                const aKey = a[1].key;
                const bKey = b[1].key;
                if (aKey === 'Unknown') return 1;
                if (bKey === 'Unknown') return -1;
                return aKey.localeCompare(bKey);
            })
        );
    }, [customSort]);

    return (
        <div className="bg-secondary">
            <h2
                className={`bg-secondary bg-opacity-50 pb-2 pt-4 text-center text-2xl font-bold text-primary underline`}
            >
                {title}
            </h2>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
                {Object.entries(data)
                    .sort(sortFunction)
                    .map(([key, value], index) => (
                        <Link
                            key={key}
                            to={`/anime/${path}/${index + 1}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="xl:w-1/8 card cursor-pointer rounded-lg bg-primary text-primary-content shadow-lg transition-shadow duration-300 hover:bg-opacity-75 hover:shadow-xl xs:w-1/3 md:w-1/4 lg:w-1/5"
                        >
                            <div className="card-body m-0.5 flex items-center justify-center p-2">
                                <h2
                                    className={`card-title text-center font-semibold leading-tight text-secondary xs:text-xs ${capitalizeTitle ? 'capitalize' : ''}`}
                                >
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
