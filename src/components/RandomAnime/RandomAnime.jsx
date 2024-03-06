import 'slick-carousel/slick/slick-theme.css';
import 'slick-carousel/slick/slick.css';

import React, { useMemo, useRef } from 'react';

import AnimeCard from '../AnimeCard/AnimeCard';
import { Link } from 'react-router-dom';
import Slider from 'react-slick';
import { shuffleRandom } from '../../recommender/recommender';

const RandomAnime = ({ anime, allAnime }) => {
    const shuffledAnime = useMemo(() => {
        const shuffled = [...allAnime];
        shuffleRandom(shuffled);
        return shuffled.slice(0, 10);
    }, [allAnime]);

    const settings = {
        dots: true,
        dotsClass: 'slick-dots slick-thumb',
        infinite: true,
        autoplay: false,
        swipeToSlide: true,
        slidesToShow: 3,
        slidesToScroll: 1,
        initialSlide: 0,
        speed: 500,
        autoplaySpeed: 2000,
        cssEase: 'linear',
        responsive: [
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 1280,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 1440,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 1536,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 1920,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 2560,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
            {
                breakpoint: 3840,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 1,
                    infinite: true,
                },
            },
        ],
    };

    return (
        <section id="random-anime" className="w-full overflow-x-hidden bg-secondary px-10 pb-8 dark:bg-gray-900">
            <div className="slider-container xs:pb-3 2xl:pb-6">
                <Slider {...settings}>
                    {shuffledAnime.map((anime, index) => (
                        <div key={anime.title} className="m-4 mx-auto flex flex-col justify-between">
                            <AnimeCard anime={anime} index={index + 1} />
                        </div>
                    ))}
                </Slider>
            </div>
            {anime !== undefined && (
                <div className="mx-auto mt-2 flex items-center justify-center">
                    <Link
                        to={`/anime/recommendations/${anime.id}`}
                        className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white lg:px-4 lg:text-xl"
                    >
                        View all recommendations
                    </Link>
                </div>
            )}
        </section>
    );
};

export default React.memo(RandomAnime);
