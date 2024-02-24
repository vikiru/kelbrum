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
        <div key={anime.title} className="card grid w-[90%] cursor-default rounded-lg bg-primary p-2 shadow-lg">
            <div className="m-5">
                <figure>
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
                <div className="card-genres mb-4 flex flex-wrap gap-2">
                    {anime.genres.map((g) => (
                        <span className="badge badge-neutral bg-gray-200 px-4 py-4 text-lg text-gray-700" key={g}>
                            {g}
                        </span>
                    ))}
                </div>
                <div className="grid gap-4 pb-4 lg:grid-cols-2">
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
                        <p className="text-base text-gray-700">{anime.episodes === 0 ? 'Unknown' : anime.episodes}</p>
                    </div>
                    <div className="rounded-lg bg-base-200 p-4 shadow-md">
                        <h2 className="text-lg font-bold text-secondary">Score</h2>
                        <p className="text-base text-gray-700">
                            {anime.score === 0 ? 'Unknown' : `${anime.score} /   10`}
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
};

export default AnimeCard;
