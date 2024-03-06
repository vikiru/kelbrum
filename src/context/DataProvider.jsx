import React, { createContext, useContext, useMemo } from 'react';

import data from '../recommender/data/entries.json';

const DataContext = createContext();

export const DataProvider = ({ children }) => {
    const state = useMemo(
        () => ({
            data: data,
        }),
        [],
    );

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

export const useData = () => useContext(DataContext);
