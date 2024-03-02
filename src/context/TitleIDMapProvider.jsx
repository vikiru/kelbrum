import React, { createContext, useContext, useMemo } from 'react';

import titleIDMap from '../recommender/data/titleIDMap.json';

const TitleIDMapContext = createContext();

export const TitleIDMapProvider = ({ children }) => {
    const state = useMemo(() => ({
        titleIDMap: titleIDMap,
    }), []);

    return <TitleIDMapContext.Provider value={state}>{children}</TitleIDMapContext.Provider>;
};

export const useTitleIDMap = () => useContext(TitleIDMapContext);
