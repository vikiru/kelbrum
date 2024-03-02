import React, { useEffect } from 'react';

import SearchBar from './../../components/SearchBar/SearchBar';
import { useTitleIDMap } from '../../context/TitleIDMapProvider';

const SearchAnime = () => {
    const { titleIDMap } = useTitleIDMap();
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
