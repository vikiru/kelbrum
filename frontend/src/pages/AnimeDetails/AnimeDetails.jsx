import React, { useEffect, useState } from 'react';
import {
    retrieveAnimeData,
    returnClusterSimilarities,
    returnRandomRecommendations,
} from '../../../../reccomender/reccomender';

import RandomAnime from './../../components/RandomAnime/RandomAnime';

const AnimeDetails = ({ anime, data, featureArray, kmeans }) => {
    const [hasError, setHasError] = useState(false);
    const [topResults, setTopResults] = useState([]);

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
        <div>
            <h2 className="bg-secondary py-4 text-center text-2xl font-bold text-primary underline">{anime.title}</h2>
            <div className="grid lg:grid-cols-2 gap-4">
                <div className="text-md m-8 text-justify">
                    <div>
                        <h2 className="pt-4 text-left text-xl font-bold text-secondary underline">
                            General Information
                        </h2>
                        <div className="card-actions my-4 flex flex-wrap gap-2">
                            {anime.genres.map((g) => (
                                <span
                                    className="badge badge-neutral bg-gray-200 px-4 py-4 text-lg text-gray-700"
                                    key={g}
                                >
                                    {g}
                                </span>
                            ))}
                            {anime.demographics.map((d) => (
                                <span
                                    className="badge badge-neutral bg-gray-200 px-4 py-4 text-lg text-gray-700"
                                    key={d}
                                >
                                    {d}
                                </span>
                            ))}
                            {anime.themes.map((t) => (
                                <span
                                    className="badge badge-neutral bg-gray-200 px-4 py-4 text-lg text-gray-700"
                                    key={t}
                                >
                                    {t}
                                </span>
                            ))}
                        </div>
                        <div className="grid gap-4 pb-4 lg:grid-cols-2">
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Type</h2>
                                <p className="text-base text-gray-700">{anime.type}</p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Season</h2>
                                <p className="text-base text-gray-700">
                                    <span className="capitalize">{anime.season === 'Unknown' ? '' : anime.season}</span>
                                    <span className="capitalize">
                                        {anime.year === 'Unknown' ? '' : ` ${anime.year}`}
                                    </span>
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Rating</h2>
                                <p className="text-base text-gray-700">{anime.rating}</p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Episodes</h2>
                                <p className="text-base text-gray-700">
                                    {anime.episodes === '0' ? 'Unknown' : anime.episodes}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Score</h2>
                                <p className="text-base text-gray-700">
                                    {anime.score === '0' ? 'Unknown' : `${anime.score} /  10`}
                                </p>
                            </div>
                        </div>
                    </div>
                    <p className='text-left'>{anime.synopsis}</p>
                    <div>
                        <h2 className="pt-4 text-left text-xl font-bold text-secondary underline">
                            Additional Information
                        </h2>
                        <div className="grid lg:grid-cols-2 gap-4">
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Studios</h2>
                                <p className="text-base text-gray-700">
                                    {anime.studios.length === 0 ? 'Unknown' : anime.studios.join(', ')}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Producers</h2>
                                <p className="text-base text-gray-700">
                                    {anime.producers.length === 0 ? 'Unknown' : anime.producers.join(', ')}
                                </p>
                            </div>
                            <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                <h2 className="text-lg font-bold text-secondary">Licensors</h2>
                                <p className="text-base text-gray-700">
                                    {anime.licensors.length === 0 ? 'Unknown' : anime.licensors.join(', ')}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h2 className="py-4 text-left text-xl font-bold text-secondary underline">External Links</h2>
                        <div className="flex space-x-2">
                            <button className="rounded-lg bg-gray-200 p-2 transition-colors duration-200 hover:bg-gray-400">
                                <a href={anime.pageURL} target="_blank" rel="noopener noreferrer">
                                    <img
                                        src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/myanimelist.svg"
                                        className="h-10 w-10 rounded-lg object-cover"
                                        alt="MyAnimeList Icon"
                                    />
                                </a>
                            </button>
                            <button className="rounded-lg bg-gray-200 p-2 transition-colors duration-200 hover:bg-gray-400">
                                <a href={anime.trailerURL} target="_blank" rel="noopener noreferrer">
                                    <img
                                        src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/youtube.svg"
                                        className="h-10 w-10 rounded-lg object-cover"
                                        alt="YouTube Icon"
                                    />
                                </a>
                            </button>
                        </div>
                    </div>
                </div>

                <div className="container m-4 mx-auto">
                    <figure>
                        {!hasError && (
                            <img
                                src={anime.imageURL}
                                alt={`${anime.title} image`}
                                className="h-full w-full rounded-lg object-cover"
                                style={{
                                    maxWidth: '100%',
                                    maxHeight: '50%',
                                }}
                            />
                        )}
                    </figure>
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