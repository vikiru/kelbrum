import { debounce } from 'lodash';
import React, { useEffect, useState } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import { useParams } from 'react-router-dom';

import { useData } from '../../context/DataProvider';
import AnimeCard from './../../components/AnimeCard/AnimeCard';

const InfinitePagination = () => {
    const { path, id } = useParams();
    const index = id - 1;

    const [items, setItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 50;
    const itemsPerFetch = 10;

    useEffect(() => {
        const allItemsLoaded = items.length >= sortedData.length;
        setHasMore(!allItemsLoaded);
    }, [items, sortedData.length]);

    const fetchAnimeItems = () => {
        const startIndex = (currentPage - 1) * itemsPerFetch;
        const endIndex = startIndex + itemsPerFetch;
        const newItems = sortedData.slice(startIndex, endIndex);

        if (newItems.length === 0 || items.length + newItems.length >= itemsPerPage) {
            setHasMore(false);
        }

        return newItems;
    };

    const fetchMoreData = () => {
        if (items.length >= itemsPerPage) {
            setHasMore(false);
            return;
        }

        const newItems = fetchAnimeItems();
        setItems((prevItems) => [...prevItems, ...newItems]);
    };

    const handlePageChange = (newPage) => {
        setCurrentPage(newPage);
        const newItems = fetchAnimeItems();
        setItems(newItems);

        window.scrollTo({
            top: 0,
            behavior: 'smooth',
        });
    };

    useEffect(() => {
        const initialItems = fetchAnimeItems();
        setItems(initialItems);
    }, [currentPage]);

    return (
        <div className="bg-secondary pb-6">
            <h2 className="bg-secondary pb-4 pt-6 text-center text-4xl font-bold text-primary underline">{title}</h2>
            <InfiniteScroll
                pageStart={0}
                loadMore={debounce(fetchMoreData, 1000)}
                hasMore={hasMore}
                loader={
                    <div key={0} className="flex h-10 items-center justify-center">
                        {hasMore && <div className="loading loading-lg bg-primary" />}
                    </div>
                }
            >
                <div className="3xl:grid-cols-3 m-8 grid gap-4 p-2 xs:grid-cols-1 lg:grid-cols-2">
                    {items.map((item, index) => {
                        const globalIndex = (currentPage - 1) * itemsPerFetch + index + 1;
                        return <AnimeCard key={item.id} anime={item} index={globalIndex} />;
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
