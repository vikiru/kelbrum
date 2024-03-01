import React, { useEffect, useState } from 'react';

import AnimeCard from '../AnimeCard/AnimeCard';
import { Link } from 'react-router-dom';
import { shuffleRandom } from '../../recommender/recommender';

const AnimeItem = ({ anime, index }) => {
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
        const img = new Image();
        img.src = anime.imageURL;
        img.onerror = () => setHasError(true);
        img.onload = () => setHasError(false);
    }, [anime.imageURL]);

    return (
        <div key={anime.title} className="m-4 flex flex-col justify-start">
            <AnimeCard anime={anime} index={index + 1} />
        </div>
    );
};

const RandomAnime = ({ anime, allAnime }) => {
    const shuffledAnime = [...allAnime];
    shuffleRandom(shuffledAnime);
    const randomAnime = shuffledAnime.slice(0, 10);

    return (
        <div className="w-full  bg-secondary pb-8 dark:bg-gray-900">
            <div className="grid w-full px-4 py-6 grid-cols-1 lg:grid-cols-2 3xl:grid-cols-3">
                {randomAnime.map((anime, index) => (
                    <AnimeItem key={anime.title} anime={anime} index={index} />
                ))}
            </div>
            {anime !== undefined && (
                <div className="mt-2 flex items-center justify-center">
                    <Link
                        to={`/anime/recommendations/${anime.id}`}
                        className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white"
                    >
                        View all recommendations
                    </Link>
                </div>
            )}
        </div>
    );
};

export default React.memo(RandomAnime);