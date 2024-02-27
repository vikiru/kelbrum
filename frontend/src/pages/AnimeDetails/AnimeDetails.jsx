import React, { useEffect, useMemo, useState } from 'react';
import {
    retrieveAnimeData,
    returnClusterSimilarities,
    returnRandomRecommendations,
} from '../../../../reccomender/reccomender';

import RandomAnime from './../../components/RandomAnime/RandomAnime';
import { useData } from '../../context/DataProvider';
import { useParams } from 'react-router-dom';

const AnimeDetails = () => {
    const { data, featureArray, kmeans } = useData();
    const { id } = useParams();
    const anime = data[id];
    const [hasError, setHasError] = useState(false);
    const [topResults, setTopResults] = useState([]);

    const trimmedStudios = useMemo(() => {
        return anime.studios.length === 0 ? ['Unknown'] : anime.studios.map((studio) => studio.trim());
    }, [anime.studios]);

    const trimmedProducers = useMemo(() => {
        return anime.producers.length === 0 ? ['Unknown'] : anime.producers.map((producer) => producer.trim());
    }, [anime.producers]);

    const trimmedLicensors = useMemo(() => {
        return anime.licensors.length === 0 ? ['Unknown'] : anime.licensors.map((licensor) => licensor.trim());
    }, [anime.licensors]);

    useEffect(() => {
        const img = new Image();
        img.src = anime.imageURL;
        img.onerror = () => setHasError(true);
        img.onload = () => setHasError(false);
    }, [anime.imageURL]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const cluster = kmeans.clusters[anime.id];
                const results = await returnClusterSimilarities(cluster, kmeans.clusters, featureArray, anime.id);
                const reccs = await returnRandomRecommendations(results);
                const topResultsData = await retrieveAnimeData(reccs, data);
                setTopResults(topResultsData);
            } catch (error) {
                console.error('Failed to fetch data:', error);
                setTopResults([]);
                setHasError(true);
            }
        };

        fetchData();
    }, [anime.id, data, featureArray, kmeans.clusters]);

    return (
        <div className="overflow-x-hidden">
            <h2 className="bg-secondary py-4 text-center text-2xl font-bold text-primary underline">{anime.title}</h2>
            <div className="grid gap-4 lg:grid-cols-2">
                <div className="text-md mx-8 text-justify">
                    <div className="mx-4 mt-4 lg:hidden">
                        <figure>
                            {!hasError && (
                                <img
                                    src={anime.imageURL}
                                    alt={`${anime.title} image`}
                                    className="h-[80%] w-full rounded-lg border-2 border-gray-300 object-contain shadow-sm transition-shadow duration-300 hover:shadow-xl"
                                />
                            )}
                        </figure>
                    </div>
                    <div>
                        <h2 className="pt-4 text-left text-xl font-bold text-secondary underline">
                            General Information
                        </h2>
                        <div className="3xl:grid-cols-2 mt-4 grid gap-4 pb-4">
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Type</h2>
                                <p className="text-base text-neutral">{anime.type}</p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Source</h2>
                                <p className="text-base text-neutral">{anime.source}</p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Season</h2>
                                <p className="text-base text-neutral">
                                    {anime.season === 'Unknown' && anime.year === 'Unknown' ? (
                                        'Unknown'
                                    ) : (
                                        <>
                                            <span className="capitalize">{anime.season}</span>
                                            <span className="capitalize">
                                                {anime.year !== 'Unknown' && ` ${anime.year}`}
                                            </span>
                                        </>
                                    )}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Rating</h2>
                                <p className="text-base text-neutral">{anime.rating}</p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Episodes</h2>
                                <p className="text-base text-neutral">
                                    {anime.episodes === '0' ? 'Unknown' : anime.episodes}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Score</h2>
                                <p className="text-base text-neutral">
                                    {anime.score === '0' ? 'Unknown' : `${anime.score} /  10`}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="container mx-4 mt-14 xs:hidden lg:block">
                    <figure>
                        {!hasError && (
                            <img
                                src={anime.imageURL}
                                alt={`${anime.title} image`}
                                className="h-[50%] w-[80%] max-w-full rounded-lg border-2 border-gray-300 object-contain shadow-sm transition-shadow duration-300 hover:shadow-xl"
                            />
                        )}
                    </figure>
                </div>
            </div>

            <div className="flex flex-col gap-4 lg:flex-row">
                <div className="text-md mx-8 text-justify">
                    <div>
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline">Synopsis</h2>
                        <p className="text-left">{anime.synopsis}</p>
                    </div>
                    <div>
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline">
                            Additional Information
                        </h2>
                        <div className="grid gap-4">
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Tags</h2>
                                <p className="text-base text-neutral">
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
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Studios</h2>
                                <p className="text-base text-neutral">
                                    {trimmedStudios.map((studio, index) => (
                                        <span key={index}>
                                            {studio}
                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Producers</h2>
                                <p className="text-base text-neutral">
                                    {trimmedProducers.map((producer, index) => (
                                        <span key={index}>
                                            {producer}
                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Licensors</h2>
                                <p className="text-base text-neutral">
                                    {trimmedLicensors.map((licensor, index) => (
                                        <span key={index}>
                                            {licensor}
                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Synonyms</h2>
                                <p className="text-base text-neutral">
                                    {anime.titles.map((synonym, index) => (
                                        <span key={index}>
                                            {synonym}
                                            <br />
                                        </span>
                                    ))}
                                </p>
                            </div>
                        </div>
                    </div>
                    <div>
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline">Statistics</h2>
                        <div className="stats w-full bg-base-200 shadow xs:stats-vertical xl:stats-horizontal xl:w-auto">
                            <div className="stat">
                                <div className="stat-title text-secondary">Rank</div>
                                <div className="stat-value text-xl font-medium text-neutral">
                                    # {anime.rank === 0 ? 'Unknown' : anime.rank}
                                </div>
                            </div>
                            <div className="stat">
                                <div className="stat-title text-secondary">Popularity</div>
                                <div className="stat-value text-xl font-medium text-neutral">
                                    # {anime.popularity === 0 ? 'Unknown' : anime.popularity}
                                </div>
                            </div>
                            <div className="stat">
                                <div className="stat-title text-secondary">Total Favourites</div>
                                <div className="stat-value text-xl font-medium text-neutral">
                                    {anime.favourites === 0 ? 'Unknown' : anime.favourites}
                                </div>
                            </div>
                            <div className="stat">
                                <div className="stat-title text-secondary">Total Members</div>
                                <div className="stat-value text-xl font-medium text-neutral">
                                    {anime.members === 0 ? 'Unknown' : anime.members}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="pb-6">
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline">External Links</h2>
                        <div className="flex space-x-2">
                            {anime.pageURL !== 'Unknown' && (
                                <button className="rounded-lg bg-base-200 p-2 transition-colors duration-200 hover:bg-neutral-400">
                                    <a href={anime.pageURL} target="_blank" rel="noopener noreferrer">
                                        <img
                                            src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/myanimelist.svg"
                                            className="h-10 w-10 rounded-lg object-cover"
                                            alt="MyAnimeList Icon"
                                        />
                                    </a>
                                </button>
                            )}
                            {anime.trailerURL !== 'Unknown' && (
                                <button className="rounded-lg bg-base-200 p-2 transition-colors duration-200 hover:bg-neutral-400">
                                    <a href={anime.trailerURL} target="_blank" rel="noopener noreferrer">
                                        <img
                                            src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/youtube.svg"
                                            className="h-10 w-10 rounded-lg object-cover"
                                            alt="YouTube Icon"
                                        />
                                    </a>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            <div>
                <h2 className="bg-secondary py-4 text-center text-4xl font-bold text-primary underline">
                    Unique Random Suggestions
                </h2>
                <RandomAnime allAnime={topResults} />
            </div>
        </div>
    );
};

export default AnimeDetails;
