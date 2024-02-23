import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const AnimeCard = ({ anime }) => {
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
        const img = new Image();
        img.src = anime.imageURL;
        img.onerror = () => setHasError(true);
        img.onload = () => setHasError(false);
    }, [anime.imageURL]);

    return (
        <div className="card w-[95%] p-2 bg-primary cursor-default shadow-lg rounded-lg grid lg:grid-cols-2">
            <div className="lg:m-10">
                <figure className="mb-4">
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="w-full h-full object-fill rounded-lg"
                        />
                    )}{' '}
                </figure>
            </div>
            <div className="card-body">
                <h2 className="card-title text-lg font-semibold text-secondary">{anime.title}</h2>
                <div>
                    <span className="text-lg font-medium">{anime.type}</span> |{' '}
                    <span className="text-lg text-accent font-medium">{anime.rating}</span>
                </div>

                <div className="text-sm text-secondary mb-2 flex items-center">
                    <span className="text-lg font-medium">Score: </span>
                    <span className="text-lg text-accent font-semibold ml-2">{anime.score.toFixed(1)}</span>
                    <span className="text-lg text-secondary font-semibold ml-2"> / 10</span>
                    <span className="ml-2">✨</span>
                </div>

                <div className="card-actions flex flex-wrap gap-2 mb-4">
                    {anime.genres.map((g) => (
                        <span className="badge badge-neutral bg-gray-200 text-gray-700" key={g}>
                            {g}
                        </span>
                    ))}
                    {anime.demographics.map((d) => (
                        <span className="badge badge-neutral bg-gray-200 text-gray-700" key={d}>
                            {d}
                        </span>
                    ))}
                </div>

                <div className="card-actions">
                    <button className="btn btn-accent uppercase text-white bg-accent hover:bg-accent-darker rounded-lg px-4 py-2">
                        Read more
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AnimeCard;
