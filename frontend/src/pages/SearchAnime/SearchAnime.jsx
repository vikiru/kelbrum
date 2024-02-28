import React, { useEffect } from 'react';

import { useData } from '../../context/DataProvider';
import SearchBar from './../../components/SearchBar/SearchBar';

const SearchAnime = () => {
    const { titleIDMap } = useData();
    const fields = ['title', 'synonyms'];

    useEffect(() => {
        window.scrollBy(0, 50);
    }, []);

    return (
        <div>
            <h2 className="bg-secondary py-4 text-center text-2xl font-bold text-primary underline">
                Search for an anime
            </h2>
            <SearchBar valueMap={titleIDMap} path="" fields={fields} storeFields={fields} />
        </div>
    );
};

export default React.memo(SearchAnime);
