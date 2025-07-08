import React, { useEffect } from 'react';
import SearchBar from './../../components/SearchBar/SearchBar';
import { useTitleIDMap } from '../../context/TitleIDMapProvider';

const SearchAnime = () => {
    const { titleIDMap } = useTitleIDMap();
    const fields = ['title', 'synonyms', 'type'];

    useEffect(() => {
        window.scrollBy(0, 50);
    }, []);

    return (
        <section
            className="bg-secondary pb-16 dark:bg-gray-900"
            id="anime-search"
        >
            <SearchBar
                fields={fields}
                path=""
                storeFields={fields}
                valueMap={titleIDMap}
            />
        </section>
    );
};

export default React.memo(SearchAnime);
