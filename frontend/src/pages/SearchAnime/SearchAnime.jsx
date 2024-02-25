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
            const results = miniSearch.search(string, { limit: 10 });
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
        <div className={`container min-h-screen flex-grow p-8 pb-6 ${showSuggestions ? 'overflow-y-hidden' : ''}`}>
            <div className="min-h-[40rem] flex-shrink-0">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => {
                        setInputValue(e.target.value);
                        handleOnSearch(e.target.value);
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Type to filter titles..."
                    className="input input-bordered w-full"
                />
                {suggestions.length > 0 && (
                    <div className="search-results mt-4 max-h-[20rem] space-y-2 overflow-y-hidden">
                        {suggestions.map((suggestion, index) => (
                            <div
                                key={index}
                                ref={(el) => (suggestionRefs.current[index] = el)}
                                className={`card cursor-pointer transition-shadow duration-200 hover:shadow-lg ${index === activeSuggestionIndex ? 'bg-blue-100' : ''}`}
                                onClick={() => handleOnSelect(suggestion)}
                            >
                                <div className="card-body">
                                    <p className="text-md card-title">{suggestion.title}</p>
                                    <p className="text-sm text-gray-500">{suggestion.synonyms.join(', ')}</p>
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
