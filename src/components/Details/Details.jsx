import React, { useEffect, useMemo, useState } from 'react';

const Details = ({ anime }) => {
    const [hasError, setHasError] = useState(false);
    const [webPURL, setWebPURL] = useState(anime.imageURL);

    useEffect(() => {
        setWebPURL(anime.imageURL.replace('.jpg', '.webp'));
    });

    const trimmedStudios = useMemo(() => {
        return anime.studios.length === 0 ? ['Unknown'] : anime.studios.map((studio) => studio.trim());
    }, [anime.studios]);

    const trimmedProducers = useMemo(() => {
        return anime.producers.length === 0 ? ['Unknown'] : anime.producers.map((producer) => producer.trim());
    }, [anime.producers]);

    const trimmedLicensors = useMemo(() => {
        return anime.licensors.length === 0 ? ['Unknown'] : anime.licensors.map((licensor) => licensor.trim());
    }, [anime.licensors]);

    const handleImageError = () => {
        setHasError(true);
    };

    return (
        <section id="anime-details" className="container-xl">
            <h2 className="bg-secondary pt-4 text-center text-xl font-bold text-primary underline xs:text-lg lg:text-4xl dark:bg-gray-900 dark:text-gray-100">
                {anime.title}
            </h2>

            <div className="grid gap-4 lg:grid-cols-2">
                <div className="text-md mx-8 text-justify">
                    <section id="anime-image" className="mx-4 mt-14 xs:hidden lg:hidden">
                        {!hasError && (
                            <picture>
                                <source srcSet={`${webPURL}`} type="image/webp" />
                                <source srcSet={`${anime.imageURL}`} type="image/jpeg" />
                                <img
                                    src={`${anime.imageURL}`}
                                    alt={`${anime.title} image`}
                                    className="h-auto w-full rounded-lg object-contain shadow-sm transition-shadow duration-300 hover:shadow-xl"
                                />
                            </picture>
                        )}
                    </section>

                    <section id="anime-general-info">
                        <h2 className="pt-4 text-left text-xl font-bold text-secondary underline xl:text-2xl dark:text-gray-100">
                            General Information
                        </h2>

                        <div className="mt-4 grid gap-4 pb-4">
                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Type</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral lg:text-xl dark:text-gray-100">{anime.type}</p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Source</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">{anime.source}</p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Season</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl capitalize text-neutral dark:text-gray-100">{anime.premiered}</p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Rating</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">{anime.rating}</p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Episodes</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {anime.episodes === 0 ? 'Unknown' : anime.episodes}
                                </p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Score</h2>

                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {anime.score === 0 ? 'Unknown' : `${anime.score} /  10`}
                                </p>
                            </div>
                        </div>
                    </section>
                </div>

                <section id="anime-image" className="mx-4 mt-14 xs:hidden lg:block">
                    {!hasError && (
                        <picture>
                            <source srcSet={`${webPURL}`} type="image/webp" />
                            <source srcSet={`${anime.imageURL}`} type="image/jpeg" />
                            <img
                                src={`${anime.imageURL}`}
                                alt={`${anime.title} image`}
                                className="h-auto max-h-[1500px] w-full rounded-lg object-contain shadow-sm transition-shadow duration-300 hover:shadow-xl"
                            />
                        </picture>
                    )}
                </section>
            </div>

            <div className="flex flex-col gap-4 lg:flex-row">
                <div className="text-md mx-8 text-justify">
                    <section id="anime-synopsis">
                        <h2 className="py-4 text-left text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary underline dark:text-gray-100">
                            Synopsis
                        </h2>

                        <p className="text-left text-xl lg:text-2xl dark:text-gray-100">{anime.synopsis}</p>
                    </section>

                    <section id="anime-additional-info">
                        <h2 className="py-4 text-left text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary underline dark:text-gray-100">
                            Additional Information
                        </h2>

                        <div className="grid gap-4">
                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Tags</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {anime.genres
                                        .filter((g) => g !== 'Unknown')
                                        .map((g, index) => (
                                            <span key={index}>
                                                {g}

                                                <br />
                                            </span>
                                        ))}

                                    {anime.demographics
                                        .filter((d) => d !== 'Unknown')
                                        .map((d, index) => (
                                            <span key={index}>
                                                {d}

                                                <br />
                                            </span>
                                        ))}

                                    {anime.themes
                                        .filter((t) => t !== 'Unknown')
                                        .map((t, index) => (
                                            <span key={index}>
                                                {t}
                                                <br />
                                            </span>
                                        ))}
                                </p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Studios</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {trimmedStudios.map((studio, index) => (
                                        <span key={index}>
                                            {studio}

                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Producers</h2>
                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {trimmedProducers.map((producer, index) => (
                                        <span key={index}>
                                            {producer}

                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Licensors</h2>

                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {trimmedLicensors.map((licensor, index) => (
                                        <span key={index}>
                                            {licensor}

                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>

                            <div className="rounded-lg bg-base-200 p-4 shadow-md dark:bg-gray-600">
                                <h2 className="text-xl lg:text-2xl 4xl:text-3xl font-bold text-secondary">Synonyms</h2>

                                <p className="text-lg lg:text-xl xl:text-2xl text-neutral dark:text-gray-100">
                                    {anime.titles.map((synonym, index) => (
                                        <span key={index}>
                                            {synonym}

                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>
                        </div>
                    </section>

                    <section id="anime-statistics">
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline dark:text-gray-100">
                            Statistics
                        </h2>

                        <div className="stats w-full bg-base-200 shadow xs:stats-vertical xl:stats-horizontal xl:w-auto dark:bg-gray-600">
                            <div className="stat">
                                <div className="stat-title text-secondary text-xl lg:text-2xl 4xl:text-3xl">Rank</div>

                                <div className="stat-value text-lg lg:text-xl xl:text-2xl font-medium text-neutral dark:text-gray-100">
                                    {anime.rank === 0 ? 'Unknown' : `# ${anime.rank}`}
                                </div>
                            </div>

                            <div className="stat">
                                <div className="stat-title text-secondary text-xl lg:text-2xl 4xl:text-3xl">Popularity</div>

                                <div className="stat-value text-lg lg:text-xl xl:text-2xl font-medium text-neutral dark:text-gray-100">
                                    {anime.popularity === 0 ? 'Unknown' : `# ${anime.popularity}`}
                                </div>
                            </div>

                            <div className="stat">
                                <div className="stat-title text-secondary text-xl lg:text-2xl 4xl:text-3xl">Total Favourites</div>

                                <div className="stat-value text-lg lg:text-xl xl:text-2xl font-medium text-neutral dark:text-gray-100">
                                    {anime.favourites === 0 ? 'Unknown' : anime.favourites}
                                </div>
                            </div>

                            <div className="stat">
                                <div className="stat-title text-secondary text-xl lg:text-2xl 4xl:text-3xl">Total Members</div>

                                <div className="stat-value text-lg lg:text-xl xl:text-2xl font-medium text-neutral  dark:text-gray-100">
                                    {anime.members === 0 ? 'Unknown' : anime.members}
                                </div>
                            </div>
                        </div>
                    </section>

                    <section id="anime-external-links">
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline dark:text-gray-100">
                            External Links
                        </h2>

                        <div className="flex space-x-2  pb-6">
                            {anime.pageURL !== 'Unknown' && (
                                <button className="rounded-lg bg-base-200 p-2 transition-colors duration-200 hover:bg-neutral-400 dark:bg-gray-600">
                                    <a href={anime.pageURL} target="_blank" rel="noopener noreferrer">
                                        <img
                                            src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/myanimelist.svg"
                                            className="h-10 w-10 rounded-lg object-cover lg:h-20 lg:w-20"
                                            alt="MyAnimeList Icon"
                                        />
                                    </a>
                                </button>
                            )}

                            {anime.trailerURL !== 'Unknown' && (
                                <button className="rounded-lg bg-base-200 p-2 transition-colors duration-200 hover:bg-neutral-400 dark:bg-gray-600">
                                    <a href={anime.trailerURL} target="_blank" rel="noopener noreferrer">
                                        <img
                                            src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/youtube.svg"
                                            className="h-10 w-10 rounded-lg object-cover lg:w-20"
                                            alt="YouTube Icon"
                                        />
                                    </a>
                                </button>
                            )}
                        </div>
                    </section>
                </div>
            </div>
        </section>
    );
};

export default React.memo(Details);
