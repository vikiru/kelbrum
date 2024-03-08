import React, { useEffect, useState } from 'react';

import { Link } from 'react-router-dom';

const AnimeCard = ({ anime, index }) => {
    const excludedURL = 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png';
    const [hasError, setHasError] = useState(anime.imageURL === excludedURL);

    const handleImageError = () => {
        setHasError(true);
    };

    return (
        <div className="card mx-auto flex cursor-default flex-col overflow-hidden rounded-lg bg-primary p-4 shadow-lg xs:w-full 2xl:w-[70%] dark:bg-gray-800">
            <div className="flex flex-grow flex-col">
                <section id="title" className="flex flex-col items-center justify-center">
                    <h2 className="text-center text-lg font-semibold text-neutral 4xl:text-4xl dark:text-gray-100">
                        {anime.title.length > 32 ? anime.title.substring(0, 32) + '...' : anime.title}
                    </h2>
                </section>

                <section id="image" className="mt-4 flex justify-center">
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="h-auto w-full rounded-lg object-contain 2xl:h-[500px] 4xl:h-[800px]"
                            loading="lazy"
                            onError={handleImageError}
                        />
                    )}
                    {hasError && <div className="h-64 w-full rounded-lg bg-gray-200 dark:bg-gray-800"></div>}
                </section>

                <section id="genres" className="mt-6 flex flex-wrap items-center justify-center">
                    {anime.genres
                        .filter((g) => g !== 'Unknown')
                        .map((g) => (
                            <span
                                className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-lg sm:p-4 lg:text-xl 3xl:p-3 3xl:text-xl 4xl:p-4 4xl:text-4xl"
                                key={g}
                            >
                                {g}
                            </span>
                        ))}

                    {anime.demographics
                        .filter((d) => d !== 'Unknown')
                        .map((d) => (
                            <span
                                className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-lg sm:p-4 lg:text-xl 3xl:p-3 3xl:text-xl 4xl:p-4 4xl:text-4xl"
                                key={d}
                            >
                                {d}
                            </span>
                        ))}
                </section>
            </div>

            <section id="read-more" className="mt-4 flex justify-center">
                <Link
                    to={`/anime/${anime.id}`}
                    className="btn btn-accent rounded-lg bg-accent px-4 py-2 uppercase text-white"
                    aria-label={`Read more about ${anime.title}`}
                >
                    Read more
                </Link>
            </section>
        </div>
    );
};

export default AnimeCard;
