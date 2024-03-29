import React, { useEffect } from 'react';

import { useTitleIDMap } from '../../context/TitleIDMapProvider';
import SearchBar from './../../components/SearchBar/SearchBar';

const SearchAnime = () => {
    const { titleIDMap } = useTitleIDMap();
    const fields = ['title', 'synonyms', 'type'];

    useEffect(() => {
        window.scrollBy(0, 50);
    }, []);

    return (
        <section id="anime-search" className="bg-secondary pb-16 dark:bg-gray-900">
            <SearchBar valueMap={titleIDMap} path="" fields={fields} storeFields={fields} />
        </section>
    );
};

export default React.memo(SearchAnime);
