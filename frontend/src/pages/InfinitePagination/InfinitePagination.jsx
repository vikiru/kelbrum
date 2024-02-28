import React, { useEffect, useState } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';

import AnimeCard from '../../components/AnimeCard/AnimeCard';
import { useData } from '../../context/DataProvider';

const InfinitePagination = () => {
    const { id } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const parentPathSegments = location.pathname.split('/');
    const parentPath = parentPathSegments[2];
    const {
        filteredGenres,
        filteredThemes,
        filteredDemographics,
        filteredProducers,
        filteredStudios,
        filteredLicensors,
        filteredSeasons,
    } = useData();

    const [currentPage, setCurrentPage] = useState(1);

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const pageParam = searchParams.get('page');
        const page = pageParam ? parseInt(pageParam, 10) : 1;
        setCurrentPage(page);
    }, [location.search]);

    let data;
    switch (parentPath) {
        case 'genres':
            data = filteredGenres[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'themes':
            data = filteredThemes[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'demographics':
            data = filteredDemographics[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'producers':
            data = filteredProducers[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'studios':
            data = filteredStudios[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'licensors':
            data = filteredLicensors[id ? parseInt(id, 10) - 1 : 0];
            break;
        case 'seasons':
            data = filteredSeasons[id ? parseInt(id, 10) - 1 : 0];
            break;
        default:
            data = null;
    }

    const [items, setItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const [chunks, setChunks] = useState(0);
    const itemsPerPage = 50;
    const itemsPerFetch = 10;

    const title = `Top ${parentPath} Anime`;
    const sortedData = data.values.sort((a, b) => b.score - a.score);

    useEffect(() => {
        const allItemsLoaded = items.length >= sortedData.length;
        setHasMore(!allItemsLoaded);
    }, [items, sortedData.length]);

    const fetchAnimeItems = () => {
        const startIndex = (currentPage - 1) * itemsPerPage + chunks;

        const endIndex = Math.min(startIndex + itemsPerFetch, sortedData.length);

        const newItems = sortedData.slice(startIndex, endIndex);

        setChunks((prevChunks) => prevChunks + itemsPerFetch);

        return newItems;
    };

    const fetchMoreData = () => {
        if (items.length >= itemsPerPage) {
            setHasMore(false);
            return;
        }
        setChunks((prevChunks) => prevChunks + itemsPerFetch);
        const newItems = fetchAnimeItems();
        setItems((prevItems) => [...prevItems, ...newItems]);
    };

    const handlePageChange = (newPage) => {
        setCurrentPage(newPage);
        setChunks(0);
        navigate(`?page=${newPage}`);
        const newItems = fetchAnimeItems();
        setItems(newItems);
    };

    return (
        <div className="bg-secondary pb-6">
            <h2 className="bg-secondary pb-4 pt-6 text-center text-4xl font-bold text-primary underline">{title}</h2>
            <InfiniteScroll
                pageStart={0}
                loadMore={fetchMoreData}
                hasMore={hasMore}
                loader={
                    <div key={0} className="flex h-10 items-center justify-center">
                        {hasMore && <div className="loading loading-lg bg-primary" />}
                    </div>
                }
            >
                <div className="3xl:grid-cols-3 m-8 grid gap-4 p-2 xs:grid-cols-1 lg:grid-cols-2">
                    {items.map((item, index) => {
                        const globalIndex = (currentPage - 1) * itemsPerPage + chunks + index + 1;
                        return <AnimeCard key={item.title} anime={item} index={globalIndex} />;
                    })}
                </div>
            </InfiniteScroll>
            {!hasMore && (
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
                            Page {currentPage}
                        </button>
                        <button
                            className="btn join-item"
                            onClick={() =>
                                handlePageChange(
                                    Math.min(currentPage + 1, Math.ceil(sortedData.length / itemsPerFetch)),
                                )
                            }
                            disabled={currentPage === Math.ceil(sortedData.length / itemsPerFetch)}
                        >
                            »
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default InfinitePagination;
