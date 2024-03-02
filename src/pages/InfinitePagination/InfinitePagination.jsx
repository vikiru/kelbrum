import { debounce } from 'lodash';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
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
    const [state, setState] = useState({
        items: [],
        displayedItems: [],
        hasMore: true,
    });
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
    const sortedData = useMemo(() => {
        return data.values.sort((a, b) => b.score - a.score);
    }, [data]);
    const totalPages = Math.ceil(sortedData.length / itemsPerPage);

    useEffect(() => {
        const allItemsLoaded = state.items.length >= sortedData.length;
        setState((prevState) => ({ ...prevState, hasMore: !allItemsLoaded }));
    }, [sortedData.length, state.items]);

    useEffect(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const newItems = sortedData.slice(startIndex, endIndex);
        setState((prevState) => ({
            ...prevState,
            items: newItems,
            displayedItems: newItems.slice(0, itemsPerDisplay),
            hasMore: newItems.length > itemsPerDisplay,
        }));
    }, [currentPage, sortedData]);

    const fetchMoreItems = useCallback(
        debounce(() => {
            if (state.displayedItems.length < state.items.length) {
                const newDisplayedItems = state.displayedItems.concat(
                    state.items.slice(state.displayedItems.length, state.displayedItems.length + itemsPerDisplay),
                );
                setState((prevState) => ({
                    ...prevState,
                    displayedItems: newDisplayedItems,
                    hasMore: state.displayedItems.length + itemsPerDisplay < state.items.length,
                }));
            }
        }, 1000),
        [state.displayedItems, state.items, itemsPerDisplay],
    );

    const handlePageChange = useCallback(
        (newPage) => {
            if (newPage >= 1 && newPage <= totalPages) {
                setCurrentPage(newPage);
                navigate(`?page=${newPage}`);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        },
        [navigate, totalPages],
    );

    const actualItemsForCurrentPage = Math.min(itemsPerPage, sortedData.length - (currentPage - 1) * itemsPerPage);
    const allItemsForCurrentPageDisplayed = state.displayedItems.length >= actualItemsForCurrentPage;

    return (
        <section id={`top-${data.key}-page-${currentPage}`} className="bg-secondary pb-6">
            <h2 className="bg-secondary pb-4 pt-6 text-center text-4xl font-bold capitalize text-primary underline">
                {title}
            </h2>
            <InfiniteScroll
                pageStart={0}
                loadMore={debounce(fetchMoreItems, 1000)}
                hasMore={state.hasMore}
                loader={
                    <div key={0} className="flex h-10 items-center justify-center">
                        {state.hasMore && <div className="loading loading-lg bg-primary" />}
                    </div>
                }
            >
                <div className="3xl:grid-cols-3 m-8 grid gap-4 p-2 xs:grid-cols-1 lg:grid-cols-2">
                    {state.displayedItems.map((item, index) => {
                        const globalIndex = (currentPage - 1) * itemsPerPage + (index + 1);
                        return <AnimeCard key={item.title} anime={item} index={globalIndex} />;
                    })}
                </div>
            </InfiniteScroll>
            {allItemsForCurrentPageDisplayed && (
                <section id="pagination" className="flex justify-center bg-secondary pb-6">
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
                </section>
            )}
        </section>
    );
};

export default React.memo(InfinitePagination);
