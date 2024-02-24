import React, { useEffect, useState } from 'react';

import AnimeCard from './../../components/AnimeCard/AnimeCard';
import InfiniteScroll from 'react-infinite-scroller';
import { debounce } from 'lodash';
import { useData } from '../../context/DataProvider';

const TopAnimePage = ({ top100Anime }) => {
    const [items, setItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);

    const fetchAnimeItems = () => {
        const nextIndex = items.length;
        const newItems = top100Anime.slice(nextIndex, nextIndex + 10);

        if (newItems.length === 0) {
            setHasMore(false);
        }

        return newItems;
    };

    const fetchMoreData = () => {
        const newItems = fetchAnimeItems();
        setItems(items.concat(newItems));
    };

    return (
        <div>
            <h2 className="bg-secondary py-4 text-center text-4xl font-bold text-primary underline">Top 100 Anime</h2>
            <InfiniteScroll
                pageStart={0}
                loadMore={debounce(fetchMoreData, 500)}
                hasMore={hasMore}
                loader={
                    <div key={0} className="flex h-10 items-center justify-center">
                        Loading...
                    </div>
                }
            >
                <div className="xs:grid-cols-1  3xl:grid-cols-3  3xl:grid-cols-5 grid gap-y-2 p-2 lg:grid-cols-2">
                    {items.map((item) => (
                        <AnimeCard key={item.id} anime={item} />
                    ))}
                </div>
            </InfiniteScroll>{' '}
        </div>
    );
};

export default TopAnimePage;
