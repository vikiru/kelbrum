import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import Details from '../../components/Details/Details';
import { useData } from '../../context/DataProvider';
import {
    retrieveAnimeData,
    returnClusterSimilarities,
    returnRandomRecommendations,
} from '../../recommender/recommender';
import RandomAnime from './../../components/RandomAnime/RandomAnime';

const AnimeDetails = () => {
    const { data, featureArray, kmeans } = useData();
    const { id } = useParams();
    const anime = useMemo(() => data[id], [id, data]);
    const [topResults, setTopResults] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const cluster = kmeans.clusters[anime.id];
                const results = await returnClusterSimilarities(cluster, kmeans.clusters, featureArray, anime.id, [
                    anime.id,
                ]);
                const reccs = await returnRandomRecommendations(results);
                const topResultsData = await retrieveAnimeData(reccs, data);
                setTopResults(topResultsData);
            } catch (error) {
                setTopResults([]);
            }
        };

        if (anime) {
            fetchData();
        }
    }, [anime]);

    return (
        <div className="overflow-x-hidden dark:bg-gray-900">
            <Details anime={anime} />
            <section id="anime-recommendations">
                <h2 className="bg-secondary py-4 text-center text-4xl font-bold text-primary underline">
                    Unique Random Suggestions
                </h2>
                <RandomAnime anime={anime} allAnime={topResults} />
            </section>
        </div>
    );
};

export default React.memo(AnimeDetails);
