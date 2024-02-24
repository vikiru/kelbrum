import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { shuffleRandom } from '../../../../reccomender/reccomender';
import AnimeCard from '../AnimeCard/AnimeCard';

const RandomAnime = ({ allAnime }) => {
    shuffleRandom(allAnime);
    const randomAnime = allAnime.slice(0, 10);

    return (
        <div>
            <div className="3xl:grid-cols-4 carousel carousel-center grid w-full gap-4 bg-secondary p-2 pb-6 md:grid-cols-2">
                {randomAnime
                    .sort((a, b) => b.score - a.score)
                    .map((anime, index) => {
                        const [hasError, setHasError] = useState(false);

                        useEffect(() => {
                            const img = new Image();
                            img.src = anime.imageURL;
                            img.onerror = () => setHasError(true);
                            img.onload = () => setHasError(false);
                        }, [anime.imageURL]);

                        return <AnimeCard key={anime.title} anime={anime} />;
                    })}
            </div>
        </div>
    );
};

export default RandomAnime;
