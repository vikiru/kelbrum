import React, { useMemo } from 'react';

import AnimeCard from '../AnimeCard/AnimeCard';
import { Link } from 'react-router-dom';
import { shuffleRandom } from '../../recommender/recommender';

const RandomAnime = ({ anime, allAnime }) => {
    const shuffledAnime = useMemo(() => {
        const shuffled = [...allAnime];
        shuffleRandom(shuffled);
        return shuffled.slice(0, 10);
    }, [allAnime]);

    return (
        <section id="random-anime" className="w-full bg-secondary pb-8 dark:bg-gray-900">
            <div className="3xl:grid-cols-3 grid w-full grid-cols-1 px-4 py-6 lg:grid-cols-2">
                {shuffledAnime.map((anime, index) => (
                    <div key={anime.title} className="m-4 flex flex-col justify-start">
                        <AnimeCard anime={anime} index={index + 1} />
                    </div>
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
        </section>
    );
};

export default React.memo(RandomAnime);
