import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

const AnimeCard = ({ anime, index }) => {
    const [hasError, setHasError] = useState(false);

    useEffect(() => {
        const img = new Image();
        img.src = anime.imageURL;
        img.onerror = () => setHasError(true);
        img.onload = () => setHasError(false);
    }, [anime.imageURL]);

    return (
        <div
            key={anime.title}
            className="card grid min-h-full min-w-[50%] max-w-full cursor-default rounded-lg bg-primary p-2 shadow-lg"
        >
            <span className="bg-accent-darker badge badge-accent absolute left-2 top-2 rounded-full p-4 text-white">
                {index}
            </span>
            <div className="mx-4 mt-4">
                <figure>
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="h-[50%] w-[50%] rounded-lg object-contain"
                        />
                    )}{' '}
                </figure>
            </div>
            <div className="card-body">
                <h2 className="card-title pb-4 text-2xl font-semibold text-secondary">{anime.title}</h2>
                <div className="card-actions mb-4">
                    {anime.genres.map((g) => (
                        <span className="badge badge-neutral bg-neutral px-4 py-4 text-lg text-primary" key={g}>
                            {g}
                        </span>
                    ))}
                    {anime.demographics.map((d) => (
                        <span className="badge badge-neutral bg-neutral px-4 py-4 text-lg text-primary" key={d}>
                            {d}
                        </span>
                    ))}
                    {anime.themes.map((t) => (
                        <span className="badge badge-neutral bg-neutral px-4 py-4 text-lg text-primary" key={t}>
                            {t}
                        </span>
                    ))}
                </div>
                <div className="grid gap-4 pb-4 lg:grid-cols-2">
                    <div className="rounded-lg bg-base-200 p-4 shadow-md">
                        <h2 className="text-lg font-bold text-secondary">Type</h2>
                        <p className="text-base text-neutral">{anime.type}</p>
                    </div>
                    <div className="rounded-lg bg-base-200 p-4 shadow-md">
                        <h2 className="text-lg font-bold text-secondary">Rating</h2>
                        <p className="text-base text-neutral">{anime.rating}</p>
                    </div>
                    <div className="rounded-lg bg-base-200 p-4 shadow-md">
                        <h2 className="text-lg font-bold text-secondary">Episodes</h2>
                        <p className="text-base text-neutral">{anime.episodes === 0 ? 'Unknown' : anime.episodes}</p>
                    </div>
                    <div className="rounded-lg bg-base-200 p-4 shadow-md">
                        <h2 className="text-lg font-bold text-secondary">Score</h2>
                        <p className="text-base text-neutral">
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
