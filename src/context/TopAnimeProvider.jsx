import React, { createContext, useContext, useMemo, useRef } from 'react';

import data from '../recommender/data/entries.json';

const TopAnimeContext = createContext();

const TopAnimeProvider = ({ children }) => {
    const dataRef = useRef(data);
    const topAnime = [...dataRef.current].sort((a, b) => b.score - a.score).slice(0, 100);
    const topAnimeRef = useRef(topAnime);

    const state = useMemo(
        () => ({
            topAnime: topAnimeRef.current,
        }),
        [],
    );

    return <TopAnimeContext.Provider value={state}>{children}</TopAnimeContext.Provider>;
};

const useTopAnime = () => useContext(TopAnimeContext);

export { TopAnimeProvider, useTopAnime };
