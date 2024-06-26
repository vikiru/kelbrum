import React from 'react';
import { Link } from 'react-router-dom';

const DataCard = ({ path, index, value, capitalizeTitle = false }) => {
    return (
        <Link
            key={index}
            to={`/anime/${path}/${index + 1}`}
            id="data-card"
            className="xl:w-1/8 card cursor-pointer rounded-lg bg-primary text-primary-content shadow-lg transition-shadow duration-300 hover:bg-opacity-75 hover:shadow-xl xs:w-1/3 md:w-1/4 lg:w-1/5 dark:bg-gray-800"
        >
            <div className="card-body m-0.5 flex items-center justify-center p-2">
                <h2
                    className={`card-title text-center font-semibold leading-tight text-secondary xs:text-xs lg:text-lg 3xl:text-xl 4xl:text-2xl dark:text-gray-100 ${capitalizeTitle ? 'capitalize' : ''}`}
                >
                    {value.key} ({value.values.length})
                </h2>
            </div>
        </Link>
    );
};

export default DataCard;
