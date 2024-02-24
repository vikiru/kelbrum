// SearchBar.js
import React, { useState } from 'react';
import ReactSearchAutocomplete from 'react-search-autocomplete';

import useData from '../../context/DataProvider';

const SearchBar = () => {
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const { data, titleIDMap } = useData();

    const items = titleIDMap.map((item) => ({ id: item.value, name: item.title, synonyms: item.synonyms }));

    const normalizeString = (str) =>
        str
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '');

    const handleOnSearch = (string) => {
        const newSuggestions = items.filter((item) => {
            const itemStr = normalizeString(item.name);
            const stringStr = normalizeString(string);
            const nameMatches = itemStr.includes(stringStr);
            const synonymsMatch = item.synonyms.some((synonym) => normalizeString(synonym).includes(stringStr));
            return nameMatches || synonymsMatch;
        });
        const sortedSuggestions = newSuggestions.sort((a, b) => {
            return a.id - b.id;
        });
        setSuggestions(sortedSuggestions);
    };

    const handleOnSelect = (selectedItem) => {
        setInputValue(selectedItem.name);
        setSuggestions([]);
    };

    const formatResult = (item) => (
        <div className="cursor-pointer p-2 hover:bg-neutral">
            <span>{item.name}</span>
        </div>
    );

    return (
        <div className="container min-h-screen flex-grow">
            <div className="min-h-[20rem] flex-shrink-0">
                <ReactSearchAutocomplete
                    items={suggestions}
                    onSearch={handleOnSearch}
                    onSelect={handleOnSelect}
                    formatResult={formatResult}
                    maxResults={6}
                    placeholder="Type to filter titles..."
                    className="w-full rounded-md border-gray-300 p-2 focus:border-blue-500 focus:outline-none"
                    autocompleteItemClassName="p-2 hover:bg-neutral cursor-pointer"
                    autocompleteItemActiveClassName="bg-blue-500 text-white"
                />
            </div>
        </div>
    );
};

export default SearchBar;
