import React from 'react';
import { Link } from 'react-router-dom';

import RandomAnime from '../../components/RandomAnime/RandomAnime';
import { useData } from '../../context/DataProvider';

function Home() {
    const { data } = useData();

    return (
        <div>
            <div className="hero flex min-h-screen items-center justify-center bg-primary">
                <div className="hero-content text-center">
                    <div className="mx-auto max-w-md">
                        <h1 className="text-5xl font-bold">Discover Your Next Favourite Anime</h1>
                        <p className="py-6 text-lg">
                            Tired of searching for a new anime or trying to find a new movie to watch but can't find one
                            that suits your taste? Look no further! Search for one of your favorites, and you'll be
                            presented with a selection of similar anime, tailored just for you. Not happy with the
                            suggestions? Refresh and you'll be presented with even more!
                        </p>
                        <div className="flex justify-center space-x-4">
                            <Link to="/anime/search" className="btn btn-accent w-full rounded-lg px-6 py-3 text-white">
                                Start Your Journey
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
            <div>
                <h2 className="bg-secondary py-4 text-center text-4xl font-bold text-primary underline">
                    Random Anime
                </h2>
                <RandomAnime allAnime={data.filter((a) => a.score >= 7)} />
            </div>
        </div>
    );
}

export default React.memo(Home);
