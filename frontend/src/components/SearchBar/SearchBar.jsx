import { debounce } from 'lodash';
import MiniSearch from 'minisearch';
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SearchBar = ({ valueMap, path = '', fields, storeFields }) => {
    const [inputValue, setInputValue] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const suggestionRefs = useRef([]);

    const navigate = useNavigate();
    const navigateToPage = (id) => navigate(`/anime/${path}${id}`);

    const miniSearch = useMemo(() => {
        const miniSearch = new MiniSearch({
            fields: fields,
            storeFields: storeFields,
            searchOptions: {
                boost: { title: 2 },
                fuzzy: 0.2,
            },
        });

        miniSearch.addAll(valueMap.map((item) => ({ id: item.value, title: item.title, synonyms: item.synonyms })));
        return miniSearch;
    }, [valueMap]);

    const debouncedSearch = useCallback(
        debounce((string) => {
            const results = miniSearch.search(string, { limit: 10 });
            setSuggestions(
                results
                    .slice(0, 6)
                    .map((result) => ({ id: result.id, title: result.title, synonyms: result.synonyms })),
            );
            setActiveSuggestionIndex(0);
            setShowSuggestions(true);
        }, 300),
        [miniSearch],
    );

    const handleInputChange = (e) => {
        setInputValue(e.target.value);
        debouncedSearch(e.target.value);
    };

    const handleOnSelect = useCallback((selectedItem) => {
        setSuggestions([]);
        setInputValue(selectedItem.title);
        navigateToPage(selectedItem.id);
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
        const activeSuggestionElement = suggestionRefs.current[activeSuggestionIndex];
        if (activeSuggestionElement) {
            const container = activeSuggestionElement.parentNode;
            const containerRect = container.getBoundingClientRect();
            const elementRect = activeSuggestionElement.getBoundingClientRect();

            const isFullyVisible = elementRect.top >= containerRect.top && elementRect.bottom <= containerRect.bottom;

            if (!isFullyVisible) {
                const scrollPosition = elementRect.top - containerRect.top;
                setTimeout(() => {
                    container.scrollTop = scrollPosition;
                }, 100);
            }
        }
    }, [activeSuggestionIndex]);

    return (
        <div className={`min-h-screen flex-grow p-8 pb-16 ${showSuggestions ? 'overflow-y-hidden' : ''}`}>
            <div className="min-h-[40rem]">
                <div className="w-full">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Type to filter results..."
                        className="input input-bordered w-full p-4 pl-6 pr-6 text-sm sm:p-5 sm:pl-7 sm:pr-7 md:p-6 md:pl-8 md:pr-8 md:text-lg"
                    />
                </div>

                {suggestions.length > 0 && (
                    <div className="mt-4 max-h-[60vh] overflow-y-scroll scrollbar-thin scrollbar-track-blue-100 scrollbar-thumb-gray-500">
                        {suggestions.map((suggestion, index) => (
                            <div
                                key={index}
                                ref={(el) => (suggestionRefs.current[index] = el)}
                                className={`card cursor-pointer transition-shadow duration-200 hover:shadow-lg ${index === activeSuggestionIndex ? 'bg-blue-100' : ''}`}
                                onClick={() => handleOnSelect(suggestion)}
                            >
                                <div className="card-body p-2 sm:p-3 md:p-4">
                                    <p className="card-title text-xs sm:text-sm md:text-base">{suggestion.title}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default SearchBar;
