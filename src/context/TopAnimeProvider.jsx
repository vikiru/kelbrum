import React, { createContext, useContext, useMemo } from 'react';

import data from '../recommender/data/entries.json';

const TopAnimeContext = createContext();

export const TopAnimeProvider = ({ children }) => {
    const topAnime = useMemo(() => {
        return [...data].sort((a, b) => b.score - a.score).slice(0, 100);
    }, []);

    return <TopAnimeContext.Provider value={{ topAnime }}>{children}</TopAnimeContext.Provider>;
};

export const useTopAnime = () => useContext(TopAnimeContext);
