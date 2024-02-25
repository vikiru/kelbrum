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
            className="card grid min-h-full min-w-[50%] max-w-full cursor-default rounded-lg bg-primary p-1"
        >
            <span className="bg-accent-darker badge badge-accent absolute left-1 top-1 rounded-full p-2 text-white">
                {index}
            </span>
            <div className="grid grid-cols-2 gap-2">
                <div className="mt-6 rounded-lg bg-primary p-2">
                    {!hasError && (
                        <img
                            src={anime.imageURL}
                            alt={`${anime.title} image`}
                            className="object-fit h-46 mb-2 w-full rounded-lg object-contain"
                        />
                    )}
                </div>
                <div className="mt-4 flex flex-col justify-between rounded-lg bg-primary p-2">
                    <div>
                        <h2 className="mb-2 text-lg font-semibold text-secondary">{anime.title}</h2>
                        <div className="mb-1 flex flex-wrap">
                            {anime.genres.map((g) => (
                                <span
                                    className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs text-primary"
                                    key={g}
                                >
                                    {g}
                                </span>
                            ))}
                            {anime.demographics.map((d) => (
                                <span
                                    className="badge badge-neutral mb-1 mr-1 bg-neutral p-1 text-xs text-primary"
                                    key={d}
                                >
                                    {d}
                                </span>
                            ))}
                        </div>
                        <div className="mt-2 text-sm text-neutral">
                            <span className="font-bold">Type:</span> {anime.type}
                        </div>
                        <div className="text-sm text-neutral">
                            <span className="font-bold">Rating:</span> {anime.rating}
                        </div>
                        <div className="text-sm text-neutral">
                            <span className="font-bold">Episodes:</span> {anime.episodes}
                        </div>
                        <div className="text-sm text-neutral">
                            <span className="font-bold">Score:</span> {anime.score} / 10
                        </div>
                    </div>
                    <div className="mt-2">
                        <Link
                            to={`/anime/${anime.id}`}
                            className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white"
                        >
                            Read more
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AnimeCard;
