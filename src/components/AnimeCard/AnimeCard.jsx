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
            className="card mx-auto flex h-screen w-[80%] cursor-default justify-between rounded-lg bg-primary pb-4 p-1 dark:bg-gray-800"
        >
            <div className="pb-2">
                {' '}
                <span className="bg-accent-darker badge badge-accent absolute left-1 top-1 rounded-full p-3 text-white">
                    {index}
                </span>
            </div>

            <div className="mt-6 flex items-center justify-center pb-2">
                <h2 className="text-center text-lg font-semibold text-neutral sm:text-xl dark:text-gray-100">
                    {anime.title}
                </h2>
            </div>

            <section id="image" className="grid grid-cols-1 gap-2">
                <div className="flex justify-center rounded-lg p-2">
                    {!hasError && (
                        <picture>
                            <source srcSet={`${anime.imageURL}`} type="image/jpeg" />
                            <img
                                src={`${anime.imageURL}`}
                                alt={`${anime.title} image`}
                                className="h-48 w-full rounded-lg object-cover"
                                loading="lazy"
                                onError={handleImageError}
                            />
                        </picture>
                    )}
                </div>
            </section>

            <section id="genres" className="mt-1/2 flex flex-wrap justify-center">
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
            </section>
            <section id="read-more" className="m-2 flex justify-center">
                <Link
                    to={`/anime/${anime.id}`}
                    className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white"
                    aria-label={`Read more about ${anime.title}`}
                >
                    Read more
                </Link>
            </section>
        </section>
    );
};

export default AnimeCard;
