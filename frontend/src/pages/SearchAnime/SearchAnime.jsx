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
        <div className="bg-secondary">
            <SearchBar valueMap={titleIDMap} path="" fields={fields} storeFields={fields} />
        </div>
    );
};

export default React.memo(SearchAnime);
