import { debounce } from 'lodash/lodash.min.js';
import React, { useEffect, useState } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';

import AnimeCard from '../../components/AnimeCard/AnimeCard';
import { useData } from '../../context/DataProvider';
import {
    retrieveAnimeData,
    returnClusterSimilarities,
    returnRandomRecommendations,
} from '../../recommender/recommender';

const RecommendationsPage = () => {
    const { data, featureArray, kmeans } = useData();
    const { id } = useParams();
    const anime = data[id];
    const location = useLocation();
    const navigate = useNavigate();
    const [topResults, setTopResults] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const cluster = kmeans.clusters[anime.id];
                const results = await returnClusterSimilarities(cluster, kmeans.clusters, featureArray, anime.id);
                const reccs = await returnRandomRecommendations(results, 1000);
                const topResultsData = await retrieveAnimeData(reccs, data);
                setTopResults(topResultsData);
            } catch (error) {
                setTopResults([]);
            }
        };

        fetchData();
    }, [anime.id, data, featureArray, kmeans.clusters]);

    const [currentPage, setCurrentPage] = useState(1);
    const [items, setItems] = useState([]);
    const [displayedItems, setDisplayedItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const itemsPerPage = 50;
    const itemsPerDisplay = 10;

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const pageParam = searchParams.get('page');
        const page = pageParam ? parseInt(pageParam, 10) : 1;
        setCurrentPage(page);
    }, [location.search]);

    const title = `Top Recommendations for ${anime.title}`;
    const totalPages = Math.ceil(topResults.length / itemsPerPage);

    useEffect(() => {
        const allItemsLoaded = items.length >= topResults.length;
        setHasMore(!allItemsLoaded);
    }, [items, topResults.length]);

    useEffect(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const newItems = topResults.slice(startIndex, endIndex);
        setItems(newItems);
        setDisplayedItems(newItems.slice(0, itemsPerDisplay));
        setHasMore(newItems.length > itemsPerDisplay);
    }, [currentPage, topResults]);

    const fetchMoreItems = () => {
        if (displayedItems.length < items.length) {
            const newDisplayedItems = displayedItems.concat(
                items.slice(displayedItems.length, displayedItems.length + itemsPerDisplay),
            );
            setDisplayedItems(newDisplayedItems);
            setHasMore(displayedItems.length + itemsPerDisplay < items.length);
        }
    };

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setCurrentPage(newPage);
            navigate(`?page=${newPage}`);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    const actualItemsForCurrentPage = Math.min(itemsPerPage, topResults.length - (currentPage - 1) * itemsPerPage);
    const allItemsForCurrentPageDisplayed = displayedItems.length >= actualItemsForCurrentPage;

    return (
        <div className="bg-secondary pb-6">
            <h2 className="bg-secondary pb-4 pt-6 text-center text-4xl font-bold text-primary underline">{title}</h2>
            <InfiniteScroll
                pageStart={0}
                loadMore={debounce(fetchMoreItems, 1000)}
                hasMore={hasMore}
                loader={
                    <div key={0} className="flex h-10 items-center justify-center">
                        {hasMore && <div className="loading loading-lg bg-primary" />}
                    </div>
                }
            >
                <div className="3xl:grid-cols-3 m-8 grid gap-4 p-2 xs:grid-cols-1 lg:grid-cols-2">
                    {displayedItems.map((item, index) => {
                        const globalIndex = (currentPage - 1) * itemsPerPage + (index + 1);
                        return <AnimeCard key={item.title} anime={item} index={globalIndex} />;
                    })}
                </div>
            </InfiniteScroll>
            {allItemsForCurrentPageDisplayed && (
                <div className="flex justify-center bg-secondary pb-6">
                    <div className="join">
                        <button
                            className="btn join-item"
                            onClick={() => handlePageChange(Math.max(currentPage - 1, 1))}
                            disabled={currentPage === 1}
                        >
                            «
                        </button>
                        <button className="btn join-item" onClick={() => handlePageChange(currentPage)}>
                            Page {currentPage} of {totalPages}
                        </button>
                        <button
                            className="btn join-item"
                            onClick={() => handlePageChange(Math.min(currentPage + 1, totalPages))}
                            disabled={currentPage === totalPages}
                        >
                            »
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default React.memo(RecommendationsPage);
