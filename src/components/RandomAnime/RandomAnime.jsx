import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import { useInView } from 'react-intersection-observer';

import { shuffleRandom } from '../../recommender/recommender';
import AnimeCard from '../AnimeCard/AnimeCard';

const RandomAnime = ({ anime, allAnime }) => {
    const shuffledAnime = useMemo(() => {
        const shuffled = [...allAnime];
        shuffleRandom(shuffled);
        return shuffled.slice(0, 10);
    }, [allAnime]);

    const [ref, inView] = useInView({
        triggerOnce: true, 
    });

    const settings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 2,
        slidesToScroll: 1,
        initialSlide: 1,
        autoplay: inView, 
        autoplaySpeed: 1500,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 1,
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1,
                }
            }
        ]
    };

    return (
        <section id="random-anime" className="w-full bg-secondary pb-8 dark:bg-gray-900 overflow-x-hidden" ref={ref}>
            <Slider {...settings}>
                {shuffledAnime.map((anime, index) => (
                    <div key={anime.title} className="m-4 mx-auto flex flex-col justify-between">
                        <AnimeCard anime={anime} index={index + 1} />
                    </div>
                ))}
            </Slider>
            {anime !== undefined && (
                <div className="mt-2 flex mx-auto items-center justify-center">
                    <Link
                        to={`/anime/recommendations/${anime.id}`}
                        className="hover:bg-accent-darker btn btn-accent rounded-lg bg-accent px-2 py-1 uppercase text-white"
                    >
                        View all recommendations
                    </Link>
                </div>
            )}
        </section>
    );
};

export default React.memo(RandomAnime);
