import React from 'react';
import { Link } from 'react-router-dom';

import RandomAnime from '../../components/RandomAnime/RandomAnime';
import { useData } from '../../context/DataProvider';

function Home() {
    const { data } = useData();

    return (
        <section id="home">
            <section
                id="hero"
                className="hero flex min-h-screen items-center justify-center bg-primary dark:bg-secondary"
            >
                <div className="hero-content text-center">
                    <div className="mx-auto max-w-md xl:max-w-xl">
                        <h1 className="text-xl font-bold lg:text-5xl dark:text-gray-100">
                            Discover Your Next Favourite Anime
                        </h1>
                        <p className="py-6 text-lg md:text-xl dark:text-gray-100">
                            Tired of searching for a new anime or trying to find a new movie to watch but can't find one
                            that suits your taste? Look no further! Search for one of your favorites, and you'll be
                            presented with a selection of similar anime, tailored just for you. Not happy with the
                            suggestions? Refresh and you'll be presented with even more!
                        </p>
                        <div className="flex justify-center space-x-4 rounded-full border-b-4 border-secondary bg-accent hover:cursor-pointer dark:border-primary">
                            <Link
                                to="/anime/search"
                                className="w-full rounded-lg px-6 py-3 text-lg text-white lg:text-xl"
                            >
                                Start Your Journey
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
            <div className="bg-secondary px-4 dark:bg-gray-900">
                <h2 className="py-4 text-center text-4xl font-bold text-primary underline md:text-5xl lg:text-6xl">
                    Random Anime
                </h2>
                <RandomAnime allAnime={data.filter((a) => a.score >= 7)} />
            </div>
        </section>
    );
}

export default React.memo(Home);
