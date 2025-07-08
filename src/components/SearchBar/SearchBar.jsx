import { debounce } from 'lodash';
import MiniSearch from 'minisearch';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const SearchBar = ({ valueMap, path = '', fields, storeFields }) => {
    const [inputValue, setInputValue] = useState('');
    const [selectedType, setSelectedType] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(0);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const suggestionRefs = useRef([]);

    const navigate = useNavigate();
    const navigateToPage = (id) => navigate(`/anime/${path}${id}`);

    const miniSearchRef = useRef();

    if (!miniSearchRef.current) {
        miniSearchRef.current = new MiniSearch({
            fields: fields,
            searchOptions: {
                boost: { title: 2 },
                fuzzy: 0.2,
            },
            storeFields: storeFields,
        });
        miniSearchRef.current.addAll(
            valueMap.map((item) => ({
                id: item.value,
                synonyms: item.synonyms,
                title: item.title,
                type: item.type,
            })),
        );
    }

    const miniSearch = miniSearchRef.current;

    const debouncedSearch = useCallback(
        debounce((string) => {
            let results = miniSearch.search(string, { limit: 10 });
            if (selectedType !== '') {
                results = results.filter(
                    (result) => result.type === selectedType,
                );
            }
            setSuggestions(
                results.slice(0, 10).map((result) => ({
                    id: result.id,
                    synonyms: result.synonyms,
                    title: result.title,
                })),
            );
            setActiveSuggestionIndex(0);
            setShowSuggestions(true);
        }, 300),
        [],
    );

    const handleInputChange = useCallback(
        (e) => {
            setInputValue(e.target.value);
            debouncedSearch(e.target.value);
        },
        [debouncedSearch],
    );

    const handleOnSelect = (selectedItem) => {
        setSuggestions([]);
        setInputValue(selectedItem.title);
        navigateToPage(selectedItem.id);
        setShowSuggestions(false);
    };

    const handleKeyDown = (event) => {
        if (event.key === 'ArrowDown') {
            setActiveSuggestionIndex((prevIndex) =>
                Math.min(prevIndex + 1, suggestions.length - 1),
            );
        } else if (event.key === 'ArrowUp') {
            setActiveSuggestionIndex((prevIndex) => Math.max(prevIndex - 1, 0));
        } else if (event.key === 'Enter') {
            handleOnSelect(suggestions[activeSuggestionIndex]);
        }
    };

    useEffect(() => {
        const activeSuggestionElement =
            suggestionRefs.current[activeSuggestionIndex];
        if (activeSuggestionElement) {
            const container = activeSuggestionElement.parentNode;
            const containerRect = container.getBoundingClientRect();
            const elementRect = activeSuggestionElement.getBoundingClientRect();

            const isFullyVisible =
                elementRect.top >= containerRect.top &&
                elementRect.bottom <= containerRect.bottom;

            if (!isFullyVisible) {
                const scrollPosition = elementRect.top - containerRect.top;
                setTimeout(() => {
                    container.scrollTop = scrollPosition;
                }, 100);
            }
        }
    }, [activeSuggestionIndex]);

    useEffect(() => {
        debouncedSearch(inputValue);
    }, [debouncedSearch, inputValue]);

    return (
        <div
            className={`h-screen flex-grow p-8 pb-16 ${showSuggestions ? 'overflow-y-hidden' : ''}`}
        >
            <div className="min-h-[40rem]">
                <div className="flex justify-between">
                    <input
                        className="input input-bordered w-full flex-grow bg-white p-4 pl-6 pr-6 text-sm text-gray-900 sm:p-5 sm:pl-7 sm:pr-7 md:p-6 md:pl-8 md:pr-8 md:text-lg dark:bg-gray-800 dark:text-gray-100"
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Enter anime title"
                        type="text"
                        value={inputValue}
                    />
                    <select
                        className="select select-bordered w-1/2 max-w-xs bg-white p-2 pl-4 pr-4 text-center text-gray-900 dark:bg-gray-800 dark:text-gray-100"
                        onChange={(e) => setSelectedType(e.target.value)}
                        value={selectedType}
                    >
                        <option disabled>Select an anime type</option>
                        <option value="">All Types</option>
                        <option value="TV">TV</option>
                        <option value="ONA">ONA</option>
                        <option value="Movie">Movie</option>
                        <option value="Unknown">Unknown</option>
                    </select>
                </div>

                {suggestions.length > 0 && (
                    <div className="mt-4 max-h-[72vh] overflow-y-auto scrollbar-thin scrollbar-track-blue-100 scrollbar-thumb-gray-500 xs:space-y-1 lg:space-y-2 4xl:max-h-[80vh] dark:bg-gray-800">
                        {suggestions.map((suggestion, index) => (
                            <div
                                className={`cursor-pointer transition-shadow duration-200 hover:shadow-lg ${index === activeSuggestionIndex ? 'bg-blue-100 dark:bg-blue-500' : 'bg-white dark:bg-gray-800'}`}
                                key={index}
                                onClick={() => handleOnSelect(suggestion)}
                                ref={(el) =>
                                    (suggestionRefs.current[index] = el)
                                }
                            >
                                <div className="card-body p-2 sm:p-3 md:p-4">
                                    <p className="card-title text-lg text-gray-900 sm:text-sm lg:text-xl dark:text-gray-100">
                                        {suggestion.title}
                                    </p>
                                    {suggestion.synonyms &&
                                        suggestion.synonyms.length > 0 && (
                                            <p className="text-sm text-gray-200">
                                                {suggestion.synonyms
                                                    .slice(0, 3)
                                                    .join(', ')}
                                            </p>
                                        )}
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
