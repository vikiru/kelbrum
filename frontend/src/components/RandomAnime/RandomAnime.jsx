import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { shuffleRandom } from '../../../../reccomender/reccomender';
import AnimeCard from '../AnimeCard/AnimeCard';

const RandomAnime = ({ allAnime }) => {
    shuffleRandom(allAnime);
    const randomAnime = allAnime.slice(0, 10);

    return (
        <div className="3xl:grid-cols-4 space-2 grid w-full bg-secondary px-4 py-6 md:grid-cols-2">
            {randomAnime.map((anime, index) => {
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
            })}
        </div>
    );
};

export default RandomAnime;
