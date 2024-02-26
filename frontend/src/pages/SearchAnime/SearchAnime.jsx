import MiniSearch from 'minisearch';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useData } from '../../context/DataProvider';

const SearchAnime = () => {
    const { data, titleIDMap } = useData();
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const suggestionRefs = useRef([]);

    const navigate = useNavigate();
    const navigateToAnime = (id) => navigate(`/anime/${id}`);

    const miniSearch = useMemo(() => {
        const miniSearch = new MiniSearch({
            fields: ['title', 'synonyms'],
            storeFields: ['title', 'synonyms'],
            searchOptions: {
                boost: { title: 2 },
                fuzzy: 0.2,
            },
        });

        miniSearch.addAll(titleIDMap.map((item) => ({ id: item.value, title: item.title, synonyms: item.synonyms })));
        return miniSearch;
    }, [titleIDMap]);

    const handleOnSearch = useCallback(
        (string) => {
            const results = miniSearch.search(string, { limit: 20 });
            setSuggestions(
                results
                    .slice(0, 10)
                    .map((result) => ({ id: result.id, title: result.title, synonyms: result.synonyms })),
            );
            setActiveSuggestionIndex(0);
            setShowSuggestions(true);
        },
        [miniSearch],
    );

    const handleOnSelect = useCallback((selectedItem) => {
        setSuggestions([]);
        setInputValue(selectedItem.title);
        navigateToAnime(selectedItem.id);
        setShowSuggestions(false);
    }, []);

    const handleKeyDown = useCallback(
        (event) => {
            if (event.key === 'ArrowDown') {
                setActiveSuggestionIndex((prevIndex) => Math.min(prevIndex + 1, suggestions.length - 1));
            } else if (event.key === 'ArrowUp') {
                setActiveSuggestionIndex((prevIndex) => Math.max(prevIndex - 1, 0));
            } else if (event.key === 'Enter') {
                handleOnSelect(suggestions[activeSuggestionIndex]);
            }
        },
        [suggestions, activeSuggestionIndex],
    );

    useEffect(() => {
        if (suggestionRefs.current[activeSuggestionIndex]) {
            suggestionRefs.current[activeSuggestionIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }, [activeSuggestionIndex]);

    return (
        <div className={`min-h-screen flex-grow p-8 pb-16 ${showSuggestions ? 'overflow-y-hidden' : ''}`}>
            <div className="min-h-[40rem]">
                <div className="w-full">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => {
                            setInputValue(e.target.value);
                            handleOnSearch(e.target.value);
                        }}
                        onKeyDown={handleKeyDown}
                        placeholder="Type to filter titles..."
                        className="input input-bordered w-full p-2 pl-4 pr-4 text-sm sm:p-3 sm:pl-5 sm:pr-5 md:p-4 md:pl-6 md:pr-6 md:text-lg"
                    />
                </div>

                {suggestions.length > 0 && (
                    <div className="mt-4 max-h-60 overflow-y-auto">
                        {suggestions.map((suggestion, index) => (
                            <div
                                key={index}
                                ref={(el) => (suggestionRefs.current[index] = el)}
                                className={`card cursor-pointer transition-shadow duration-200 hover:shadow-lg ${index === activeSuggestionIndex ? 'bg-blue-100' : ''}`}
                                onClick={() => handleOnSelect(suggestion)}
                            >
                                <div className="card-body p-2 sm:p-3 md:p-4">
                                    <p className="card-title text-xs sm:text-sm md:text-base">{suggestion.title}</p>
                                    <p className="text-xs text-gray-500 sm:text-sm md:text-base">
                                        {suggestion.synonyms.slice(0, 5).join(', ')}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SearchAnime;
