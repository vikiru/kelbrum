import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick-theme.css';
import 'slick-carousel/slick/slick.css';

import { shuffleRandom } from '../../recommender/recommender';
import AnimeCard from '../AnimeCard/AnimeCard';

const RandomAnime = ({ anime, allAnime }) => {
    const shuffledAnime = useMemo(() => {
        const shuffled = [...allAnime];
        shuffleRandom(shuffled);
        return shuffled.slice(0, 10);
    }, [allAnime]);

    const settings = {
        autoplay: false,
        autoplaySpeed: 2000,
        dots: false,
        dotsClass: 'slick-dots slick-thumb mt-4',
        infinite: true,
        initialSlide: 0,
        responsive: [
            {
                breakpoint: 600,
                settings: {
                    dots: false,
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 1,
                },
            },
            {
                breakpoint: 1024,
                settings: {
                    dots: false,
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 1,
                },
            },
            {
                breakpoint: 1280,
                settings: {
                    dots: false,
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 1,
                },
            },
            {
                breakpoint: 1440,
                settings: {
                    dots: false,
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 1,
                },
            },
            {
                breakpoint: 1536,
                settings: {
                    dots: false,
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 1,
                },
            },
            {
                breakpoint: 1920,
                settings: {
                    dots: false,
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 2,
                },
            },
            {
                breakpoint: 2560,
                settings: {
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 2,
                },
            },
            {
                breakpoint: 3840,
                settings: {
                    infinite: true,
                    slidesToScroll: 1,
                    slidesToShow: 3,
                },
            },
        ],
        slidesToScroll: 1,
        slidesToShow: 3,
        speed: 500,
        swipeToSlide: true,
    };

    return (
        <section
            className="w-full overflow-x-hidden bg-secondary px-10 pb-8 dark:bg-gray-900"
            id="random-anime"
        >
            <div className="slider-container py-6">
                <Slider {...settings}>
                    {shuffledAnime.map((anime, index) => (
                        <AnimeCard
                            anime={anime}
                            index={index + 1}
                            key={anime.title}
                        />
                    ))}
                </Slider>
            </div>
            {anime !== undefined && (
                <div className="mx-auto mt-2 flex items-center justify-center pt-2">
                    <Link
                        className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white lg:px-4 lg:text-xl"
                        to={`/anime/recommendations/${anime.id}`}
                    >
                        View all recommendations
                    </Link>
                </div>
            )}
        </section>
    );
};

export default React.memo(RandomAnime);
