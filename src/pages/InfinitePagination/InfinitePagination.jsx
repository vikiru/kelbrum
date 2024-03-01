import { debounce } from 'lodash/lodash.min.js';
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

    const title = `Top ${data.key} Anime`;
    const sortedData = data.values.sort((a, b) => b.score - a.score);
    const totalPages = Math.ceil(sortedData.length / itemsPerPage);

    useEffect(() => {
        const allItemsLoaded = items.length >= sortedData.length;
        setHasMore(!allItemsLoaded);
    }, [items, sortedData.length]);

    useEffect(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const newItems = sortedData.slice(startIndex, endIndex);
        setItems(newItems);
        setDisplayedItems(newItems.slice(0, itemsPerDisplay));
        setHasMore(newItems.length > itemsPerDisplay);
    }, [currentPage, sortedData]);

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

    const actualItemsForCurrentPage = Math.min(itemsPerPage, sortedData.length - (currentPage - 1) * itemsPerPage);
    const allItemsForCurrentPageDisplayed = displayedItems.length >= actualItemsForCurrentPage;

    return (
        <div className="bg-secondary pb-6">
            <h2 className="bg-secondary pb-4 pt-6 text-center text-4xl font-bold capitalize text-primary underline">
                {title}
            </h2>
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

export default React.memo(InfinitePagination);
