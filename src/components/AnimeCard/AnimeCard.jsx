import React, { useEffect, useState } from 'react';

import { Link } from 'react-router-dom';

const AnimeCard = ({ anime, index }) => {
    const [hasError, setHasError] = useState(false);
    const [webPURL, setWebPURL] = useState(anime.imageURL);

    useEffect(() => {
        setWebPURL(anime.imageURL.replace('.jpg', '.webp'));
    }, [anime.imageURL]);

    const handleImageError = () => {
        setHasError(true);
    };

    return (
        <section
            id="anime-card"
            key={anime.id}
            className="card mx-auto flex 2xl:min-h-[20vh] xs:min-h-[60vh] w-[80%] cursor-default flex-col overflow-hidden rounded-lg bg-primary p-1 pb-4 lg:w-[90%] xl:min-h-[40vh] dark:bg-gray-800"
        >
            <div className="flex flex-col pb-8">
                <span className="bg-accent-darker badge badge-accent absolute left-2 rounded-full p-2 font-semibold text-white xs:top-10 lg:top-4 lg:p-4 lg:text-xl">
                    {index}
                </span>
            </div>

            <div className="container flex items-center justify-center pb-2 pt-2 xs:pb-0 xs:pt-6 lg:pt-4 2xl:pb-2">
                <h2 className="text-center text-lg font-semibold text-neutral xs:text-sm lg:text-2xl dark:text-gray-100">
                    {anime.title}
                </h2>
            </div>

            <section id="image" className="flex flex-col gap-2 pb-2">
                <div className="flex min-h-[50vh] 2xl:min-h-[20vh] flex-grow justify-center rounded-lg p-2">
                    {!hasError && (
                        <picture>
                            <source srcSet={`${anime.imageURL}`} type="image/jpeg" />
                            <img
                                src={`${anime.imageURL}`}
                                alt={`${anime.title} image`}
                                className="h-48 w-full rounded-lg object-cover lg:h-96"
                                loading="lazy"
                                onError={handleImageError}
                            />
                        </picture>
                    )}
                </div>
            </section>

            <section id="genres" className="flex min-h-[10vh] flex-wrap items-center justify-center xl:min-h-[5vh]">
                {anime.genres
                    .filter((g) => g !== 'Unknown')
                    .map((g) => (
                        <span
                            className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs sm:p-2 lg:text-lg 2xl:p-4  2xl:text-2xl"
                            key={g}
                        >
                            {g}
                        </span>
                    ))}

                {anime.demographics
                    .filter((d) => d !== 'Unknown')
                    .map((d) => (
                        <span
                            className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs sm:p-2  lg:text-lg 2xl:p-4 2xl:text-2xl"
                            key={d}
                        >
                            {d}
                        </span>
                    ))}
            </section>

            <section id="read-more" className="relative bottom-0 left-0 right-0 m-2 flex justify-center pt-2">
                <Link
                    to={`/anime/${anime.id}`}
                    className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white lg:px-4 lg:text-xl"
                    aria-label={`Read more about ${anime.title}`}
                >
                    Read more
                </Link>
            </section>
        </section>
    );
};

export default AnimeCard;
