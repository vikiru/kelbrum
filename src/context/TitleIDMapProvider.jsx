import React, { createContext, useContext, useMemo, useRef } from 'react';

import titleIDMap from '../recommender/data/titleIDMap.json';

const TitleIDMapContext = createContext();

export const TitleIDMapProvider = ({ children }) => {
    const titleIDMapRef = useRef(titleIDMap);

    const state = useMemo(
        () => ({
            titleIDMap: titleIDMapRef.current,
        }),
        [],
    );

    return <TitleIDMapContext.Provider value={state}>{children}</TitleIDMapContext.Provider>;
};

export const useTitleIDMap = () => useContext(TitleIDMapContext);
