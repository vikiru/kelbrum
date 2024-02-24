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
        <div className="card grid w-[95%] cursor-default rounded-lg bg-primary p-2 shadow-lg lg:grid-cols-2">
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
                    <span className="ml-2 text-lg font-semibold text-accent">{anime.score.toFixed(1)}</span>
                    <span className="ml-2 text-lg font-semibold text-secondary"> / 10</span>
                    <span className="ml-2 text-lg">✨</span>
                </div>

                <div className="card-actions mb-4 flex flex-wrap gap-2">
                    {anime.genres.map((g) => (
                        <span className="badge badge-neutral bg-gray-200 py-4 text-lg text-gray-700" key={g}>
                            {g}
                        </span>
                    ))}
                    {anime.demographics.map((d) => (
                        <span className="badge badge-neutral bg-gray-200 py-4 text-lg text-gray-700" key={d}>
                            {d}
                        </span>
                    ))}
                </div>

                <div className="card-actions">
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
};

export default AnimeCard;
