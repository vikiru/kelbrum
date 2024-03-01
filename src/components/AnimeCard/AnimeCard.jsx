import React, { useEffect, useState } from 'react';

import { Link } from 'react-router-dom';

const AnimeCard = ({ anime, index }) => {
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
        if (anime.imageURL === 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png') {
            setHasError(true);
        } else {
            const img = new Image();
            img.src = anime.imageURL;
            img.onerror = () => setHasError(true);
            img.onload = () => setHasError(false);
        }
    }, [anime.imageURL]);

    return (
        <div
            key={anime.title}
            className="card min-h-full w-full cursor-default rounded-lg bg-primary p-1 dark:bg-gray-800 flex flex-col justify-between"
        >
            <span className="bg-accent-darker badge badge-accent absolute left-1 top-1 rounded-full p-3 text-white">
                {index}
            </span>
            <div className="mt-6 flex items-center justify-center pb-2">
                <h2 className="text-center text-lg font-semibold text-neutral sm:text-xl dark:text-gray-100">
                    {anime.title}
                </h2>
            </div>
            <div className="grid grid-cols-1 gap-2 lg:grid-cols-2">
                <div className="flex justify-center rounded-lg p-2">
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="h-auto w-full rounded-lg object-contain lg:h-[80%] 2xl:h-auto 2xl:w-auto"
                        />
                    )}
                </div>
                <div className="rounded-lg flex justify-center items-center p-4 bg-gray-100 dark:bg-gray-800">
    <div>
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            <span className="font-bold">Type:</span> {anime.type}
        </div>
        <div className="text-sm font-semibold capitalize text-gray-700 dark:text-gray-300">
            <span className="font-bold ">Season:</span> {anime.premiered}
        </div>
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            <span className="font-bold">Rating:</span> {anime.rating}
        </div>
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            <span className="font-bold">Episodes:</span>{' '}
            {anime.episodes === 0 ? 'Unknown' : anime.episodes}
        </div>
        <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            <span className="font-bold">Score:</span>{' '}
            {anime.score === 0 ? 'Unknown' : `${anime.score} /   10`}
        </div>
    </div>
</div>
            </div>
            
            <div className="mt-1/2 flex flex-wrap justify-center">
    {anime.genres
        .filter((g) => g !== 'Unknown')
        .map((g) => (
            <span
                className="sm:text-xxs badge badge-neutral mb-1 mr-1 bg-neutral p-2 text-xs"
                key={g}
            >
                {g}
            </span>
        ))}
    {anime.demographics
        .filter((d) => d !== 'Unknown')
        .map((d) => (
            <span
                className="sm:text-xxs badge badge-neutral mb-1 mr-1 bg-neutral p-2 text-xs"
                key={d}
            >
                {d}
            </span>
        ))}
</div>
            <div className="mt-2 flex justify-center">
                <Link
                    to={`/anime/${anime.id}`}
                    className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white"
                >
                    Read more
                </Link>
            </div>
        </div>
    );
};

export default AnimeCard;
