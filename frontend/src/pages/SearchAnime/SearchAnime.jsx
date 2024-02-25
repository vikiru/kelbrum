import Fuse from 'fuse.js';
import { debounce } from 'lodash';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ReactSearchAutocomplete } from 'react-search-autocomplete';

import { cleanTitle } from '../../../../reccomender/utils/fetchData';

const SearchAnime = ({ data, titleIDMap }) => {
    const items = useMemo(
        () => titleIDMap.map((item) => ({ id: item.value, name: item.title, synonyms: item.synonyms })),
        [titleIDMap],
    );
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [selectedItem, setSelectedItem] = useState(null);

    const navigate = useNavigate();
    const navigateToAnime = debounce((id) => navigate(`/anime/${id}`), 500);

    const fuse = useMemo(
        () =>
            new Fuse(items, {
                keys: ['name', 'synonyms'],
                includeScore: true,
                shouldSort: true,
                threshold: 1,
                isCaseSensitive: false,
                matchAllTokens: false,
                tokenize: true,
                limit: 10,
                preprocess: {
                    name: cleanTitle,
                    synonyms: cleanTitle,
                },
            }),
        [items],
    );

    const handleOnSearch = useCallback(
        (string) => {
            const results = fuse.search(string);
            setSuggestions(results.map((result) => result.item));
        },
        [fuse],
    );

    const handleOnSelect = useCallback((selectedItem) => {
        setSuggestions([]);
        setInputValue(selectedItem.name);
        navigateToAnime(selectedItem.id);
    }, []);

    const formatResult = (item) => (
        <div className="card cursor-pointer p-2 hover:bg-neutral-300">
            <div>{item.name}</div>
        </div>
    );

    return (
        <div className="container min-h-screen flex-grow p-8 pb-6">
            <div className="min-h-[40rem] flex-shrink-0">
                <ReactSearchAutocomplete
                    items={suggestions}
                    onSearch={handleOnSearch}
                    onSelect={handleOnSelect}
                    formatResult={formatResult}
                    maxResults={10}
                    placeholder="Type to filter titles..."
                    className="text-primary-500 w-full rounded-md border-gray-300 p-2 focus:border-blue-500 focus:outline-none dark:text-current"
                    autocompleteItemClassName="p-2 hover:bg-neutral cursor-pointer"
                    autocompleteItemActiveClassName="bg-blue-500 text-white"
                />
            </div>
        </div>
    );
};

export default SearchAnime;
