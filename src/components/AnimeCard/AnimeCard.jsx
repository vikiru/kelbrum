import React, { useEffect, useState } from 'react';

import { Link } from 'react-router-dom';

const AnimeCard = ({ anime, index }) => {
    const excludedURL = 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png';
    const [hasError, setHasError] = useState(anime.imageURL === excludedURL);

    const handleImageError = () => {
        setHasError(true);
    };

    return (
        <div className="card flex flex-col cursor-default overflow-hidden rounded-lg bg-primary p-4 shadow-lg dark:bg-gray-800 xs:w-full 2xl:w-[70%] mx-auto">
            <div className="flex flex-col flex-grow">
                <section id="title" className="flex flex-col items-center justify-center">
                    <h2 className="text-center text-lg font-semibold text-neutral dark:text-gray-100 4xl:text-4xl">
                        {anime.title}
                    </h2>
                </section>

                <section id="image" className="flex justify-center mt-4">
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="w-full rounded-lg object-contain h-auto"
                            loading="lazy"
                            onError={handleImageError}
                        />
                    )}
                    {hasError && <div className="w-full h-64 rounded-lg bg-gray-200 dark:bg-gray-700"></div>}
                </section>

                <section id="genres" className="flex flex-wrap items-center justify-center mt-6">
                    {anime.genres
                        .filter((g) => g !== 'Unknown')
                        .map((g) => (
                            <span
                                className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs sm:p-2 lg:text-lg 3xl:text-xl 3xl:p-3 4xl:text-4xl 4xl:p-4"
                                key={g}
                            >
                                {g}
                            </span>
                        ))}

                    {anime.demographics
                        .filter((d) => d !== 'Unknown')
                        .map((d) => (
                            <span
                                className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs sm:p-2 lg:text-lg 3xl:text-xl 3xl:p-3 4xl:text-4xl 4xl:p-4"
                                key={d}
                            >
                                {d}
                            </span>
                        ))}
                </section>
            </div>

            <section id="read-more" className="flex justify-center mt-4">
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
