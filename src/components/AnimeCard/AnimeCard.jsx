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
            className="card flex min-h-full w-full cursor-default flex-col justify-between rounded-lg bg-primary p-1 dark:bg-gray-800"
        >
            <span className="bg-accent-darker badge badge-accent absolute left-1 top-1 rounded-full p-3 text-white">
                {index}
            </span>
            <div className="mt-6 flex items-center justify-center pb-2">
                <h2 className="text-center text-lg font-semibold text-neutral sm:text-xl dark:text-gray-100">
                    {anime.title}
                </h2>
            </div>
            <div className="grid grid-cols-1 gap-2">
                <div className="flex justify-center rounded-lg p-2">
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="h-auto w-auto rounded-lg object-contain"
                        />
                    )}
                </div>
            </div>

            <div className="mt-1/2 flex flex-wrap justify-center">
                {anime.genres
                    .filter((g) => g !== 'Unknown')
                    .map((g) => (
                        <span className="sm:text-xxs badge badge-neutral mb-1 mr-1 bg-neutral p-2 text-xs" key={g}>
                            {g}
                        </span>
                    ))}
                {anime.demographics
                    .filter((d) => d !== 'Unknown')
                    .map((d) => (
                        <span className="sm:text-xxs badge badge-neutral mb-1 mr-1 bg-neutral p-2 text-xs" key={d}>
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