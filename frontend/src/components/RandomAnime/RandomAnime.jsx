import React, { useState } from 'react';
import { Link } from 'react-router-dom';

import { shuffleRandom } from '../../../../reccomender/reccomender';
import AnimeCard from '../AnimeCard/AnimeCard';

const RandomAnime = ({ allAnime }) => {
    shuffleRandom(allAnime);
    const randomAnime = allAnime.slice(0, 10);

    return (
        <div>
            <div className="carousel carousel-center grid w-full grid-cols-3 gap-4 bg-secondary p-2 pb-6">
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
                                    <div>
                                        <span className="text-lg font-medium">{anime.type}</span> |{' '}
                                        <span className="text-lg font-medium text-accent">{anime.rating}</span>
                                    </div>
                                    <div className="mb-2 flex items-center text-sm text-secondary">
                                        <span className="text-lg font-medium">Episodes: </span>
                                        <span className="ml-2 text-lg font-semibold text-accent">{anime.episodes}</span>
                                    </div>
                                    <div className="mb-2 flex items-center text-sm text-secondary">
                                        <span className="text-lg font-medium">Score: </span>
                                        <span className="ml-2 text-lg font-semibold text-accent">
                                            {anime.score.toFixed(1)}
                                        </span>
                                        <span className="ml-2 text-lg font-semibold text-secondary"> / 10</span>
                                        <span className="ml-2 text-lg">✨</span>
                                    </div>
                                    <div className="card-actions justify-center">
                                        <Link
                                            to={`/anime/${anime.id}`}
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
