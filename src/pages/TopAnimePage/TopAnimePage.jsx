import { debounce } from 'lodash';
import { useCallback, useMemo, useState } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import AnimeCard from './../../components/AnimeCard/AnimeCard';
import { useTopAnime } from '../../context/TopAnimeProvider';

const TopAnimePage = () => {
    const { topAnime } = useTopAnime();

    const [items, setItems] = useState([]);
    const [hasMore, setHasMore] = useState(true);

    const fetchAnimeItems = useMemo(() => {
        return () => {
            const nextIndex = items.length;
            const newItems = topAnime.slice(nextIndex, nextIndex + 25);

            if (newItems.length === 0) {
                setHasMore(false);
            }

            return newItems;
        };
    }, [items, topAnime]);

    const fetchMoreData = useCallback(() => {
        const newItems = fetchAnimeItems();
        setItems((prevItems) => [...prevItems, ...newItems]);
    }, [fetchAnimeItems]);

    return (
        <section className="bg-secondary pb-6 dark:bg-gray-900" id="top-anime">
            <h2 className="bg-secondary pt-2 text-center  text-xl  font-bold text-primary underline xs:text-lg lg:text-4xl dark:bg-gray-900">
                Top 100 Anime
            </h2>
            <InfiniteScroll
                hasMore={hasMore}
                loader={
                    <div
                        className="flex h-10 items-center justify-center"
                        key={0}
                    >
                        {hasMore && (
                            <div className="loading loading-lg text-secondary dark:text-primary" />
                        )}
                    </div>
                }
                loadMore={debounce(fetchMoreData, 1000)}
                pageStart={0}
            >
                <div className="m-8 grid grid-cols-1 gap-4 p-2 lg:grid-cols-2 4xl:grid-cols-3 5xl:grid-cols-4">
                    {items.map((item, index) => (
                        <AnimeCard
                            anime={item}
                            index={index + 1}
                            key={item.id}
                        />
                    ))}
                </div>
            </InfiniteScroll>
        </section>
    );
};

export default TopAnimePage;
