import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import Details from '../../components/Details/Details';
import { useData } from '../../context/DataProvider';
import { useFeatureArray } from '../../context/FeatureArrayProvider';
import { useKMeans } from '../../context/KMeansProvider';
import {
    retrieveAnimeData,
    returnClusterSimilarities,
    returnRandomRecommendations,
} from '../../recommender/recommender';
import RandomAnime from './../../components/RandomAnime/RandomAnime';

const AnimeDetails = () => {
    const { data } = useData();
    const { featureArray } = useFeatureArray();
    const { kmeans } = useKMeans();
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
                const recommendations = await returnRandomRecommendations(results);
                const topResultsData = await retrieveAnimeData(recommendations, data);
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
                <h2 className="bg-secondary py-4 text-center text-xl font-bold text-primary underline lg:text-4xl dark:bg-gray-900">
                    Unique Random Suggestions
                </h2>
                <RandomAnime anime={anime} allAnime={topResults} />
            </section>
        </div>
    );
};

export default React.memo(AnimeDetails);
