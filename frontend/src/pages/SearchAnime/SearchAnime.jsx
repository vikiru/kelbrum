import Fuse from 'fuse.js';
import { debounce } from 'lodash';
import React, { useEffect, useMemo, useState } from 'react';
import { ReactSearchAutocomplete } from 'react-search-autocomplete';

const SearchAnime = ({ data, titleIDMap }) => {
    const items = useMemo(
        () => titleIDMap.map((item) => ({ id: item.value, name: item.title, synonyms: item.synonyms })),
        [titleIDMap],
    );
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);

    const fuse = useMemo(
        () =>
            new Fuse(items, {
                keys: ['name', 'synonyms'],
                includeScore: true,
            }),
        [items],
    );

    const handleOnSearch = (string) => {
        setInputValue(string);

        const results = fuse.search(string);

        setSuggestions(results.map((result) => result.item));
    };

    const handleOnSelect = (selectedItem) => {
        setInputValue(selectedItem.name);
        setSuggestions([]);
    };

    const formatResult = (item) => (
        <div className="card cursor-pointer p-2 hover:bg-neutral-300">
            <div>{item.name}</div>
        </div>
    );

    return (
        <div className="container min-h-screen flex-grow p-8">
            <div className="min-h-[20rem] flex-shrink-0">
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
