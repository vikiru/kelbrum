import React from 'react';
import { Link } from 'react-router-dom';

import RandomAnime from '../../components/RandomAnime/RandomAnime';
import { useData } from '../../context/DataProvider';

function Home() {
    const { data } = useData();

    return (
        <section id="home">
            <section id="hero" className="hero flex items-center justify-center bg-primary py-6 dark:bg-gray-900">
                <div className="hero-content text-center">
                    <div className="mx-auto">
                        <h1 className="text-2xl font-bold text-secondary xs:text-xl lg:text-5xl 2xl:text-6xl 3xl:text-7xl 4xl:text-8xl dark:text-gray-100">
                            Discover Your Next Favourite Anime
                        </h1>
                        <p className="xs:text-md pb-6 pt-4 text-lg text-secondary lg:text-xl xl:text-2xl 3xl:text-3xl 4xl:text-4xl 5xl:text-5xl dark:text-gray-100">
                            Tired of searching for a new anime or trying to find a new movie to watch but can't find one
                            that suits your taste? Look no further! Search for one of your favorites, and you'll be
                            presented with a selection of similar anime, tailored just for you. Not happy with the
                            suggestions? Refresh and you'll be presented with even more!
                        </p>
                        <div className="mx-auto flex items-center justify-center rounded-full border-b-4 border-secondary bg-accent py-2 pt-2 hover:cursor-pointer xs:w-full lg:w-[50%] dark:border-primary">
                            <Link to="/anime/search" className="flex-grow">
                                <span className="rounded-lg py-3 text-lg text-white lg:px-6 xl:text-2xl">
                                    Start Your Journey
                                </span>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
            <div className="bg-secondary px-4 dark:bg-gray-900">
                <h2 className="text-center font-bold text-primary underline xs:text-lg lg:text-4xl ">Random Anime</h2>
                <RandomAnime allAnime={data.filter((a) => a.score >= 7)} />
            </div>
        </section>
    );
}

export default React.memo(Home);
