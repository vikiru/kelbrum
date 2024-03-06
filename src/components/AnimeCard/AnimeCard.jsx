import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const AnimeCard = ({ anime, index }) => {
    const excludedURL = 'https://cdn.myanimelist.net/img/sp/icon/apple-touch-icon-256.png';
    const [hasError, setHasError] = useState(anime.imageURL === excludedURL);

    const handleImageError = () => {
        setHasError(true);
    };

    return (
        <section
            id="anime-card"
            key={anime.id}
            className="card mx-auto flex w-[80%] cursor-default flex-col overflow-hidden rounded-lg bg-primary p-1 pb-4 xs:min-h-[60vh] 2xl:w-[70%] dark:bg-gray-800"
        >
            <div className="flex flex-col items-center justify-center w-full">
                <h2 className="text-center text-lg font-semibold text-neutral xs:text-sm lg:text-2xl dark:text-gray-100 mb-4">
                    {anime.title}
                </h2>

                <section id="image" className="flex flex-col gap-2 pb-2">
                    <div className="flex min-h-[50vh] flex-grow justify-center rounded-lg p-2 xs:min-h-[20vh] 2xl:min-h-[20vh]">
                        {!hasError && (
                            <img
                                src={`${anime.imageURL}`}
                                alt={`${anime.title} image`}
                                className="xl:h-50 3xl:h-70 w-full rounded-lg object-contain xs:h-32 lg:h-48 4xl:h-72 5xl:h-80"
                                loading="lazy"
                                onError={handleImageError}
                            />
                        )}
                        {hasError && <div className="w-full rounded-lg bg-gray-200 lg:h-48 dark:bg-gray-800"></div>}
                    </div>
                </section>

                <section id="genres" className="flex flex-wrap items-center justify-center mb-4">
                    {anime.genres
                        .filter((g) => g !== 'Unknown')
                        .map((g) => (
                            <span
                                className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs sm:p-2 lg:text-lg"
                                key={g}
                            >
                                {g}
                            </span>
                        ))}

                    {anime.demographics
                        .filter((d) => d !== 'Unknown')
                        .map((d) => (
                            <span
                                className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs sm:p-2 lg:text-lg"
                                key={d}
                            >
                                {d}
                            </span>
                        ))}
                </section>
            </div>

            <section id="read-more" className="flex justify-center pt-2">
                <Link
                    to={`/anime/${anime.id}`}
                    className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 uppercase text-white xs:px-2 xs:py-1 xs:text-sm 3xl:px-4 3xl:py-2 3xl:text-xl"
                    aria-label={`Read more about ${anime.title}`}
                >
                    Read more
                </Link>
            </section>
        </section>
    );
};

export default AnimeCard;
