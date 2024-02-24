import React, { useState } from 'react';

import AnimeCard from '../AnimeCard/AnimeCard';
import { Link } from 'react-router-dom';
import { shuffleRandom } from '../../../../reccomender/reccomender';

const RandomAnime = ({ allAnime }) => {
    shuffleRandom(allAnime);
    const randomAnime = allAnime.filter((a) => a.score >= 7).slice(0, 10);

    return (
        <div>
            <div className="carousel carousel-center grid w-full md:grid-cols-2 3xl:grid-cols-4 gap-4 bg-secondary p-2 pb-6">
                {randomAnime
                    .sort((a, b) => b.score - a.score)
                    .map((anime, index) => {
                        const [hasError, setHasError] = useState(false);

                        const handleImageError = () => setHasError(true);
                        const handleImageLoad = () => setHasError(false);

                        return (
                            <div
                                key={anime.title}
                                className="card grid w-[90%] cursor-default rounded-lg bg-primary p-2 shadow-lg"
                            >
                                <div className="lg:m-10">
                                    <figure className="mb-4">
                                        {!hasError && (
                                            <img
                                                src={anime.imageURL}
                                                alt={`${anime.title} image`}
                                                className="h-full w-full rounded-lg object-fill"
                                            />
                                        )}{' '}
                                    </figure>
                                </div>
                                <div className="card-body">
                                    <h2 className="card-title text-2xl font-semibold text-secondary">{anime.title}</h2>
                                    <div className="grid lg:grid-cols-2 gap-4 pb-4">
                                        <div className="rounded-lg bg-base-200 p-4 shadow-md">
                                            <h2 className="text-lg font-bold text-secondary">Type</h2>
                                            <p className="text-base text-gray-700">{anime.type}</p>
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
                                    <div className="card-actions justify-center">
                                        <Link
                                            to={`/anime/${anime.id}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-4 py-2 uppercase text-white"
                                        >
                                            Read more
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
            </div>
        </div>
    );
};

export default RandomAnime;
