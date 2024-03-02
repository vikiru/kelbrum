import React, { createContext, useContext, useEffect, useMemo, useRef } from 'react';

import data from '../recommender/data/entries.json';

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const dataRef = useRef(data);

    const state = useMemo(
        () => ({
            data: dataRef.current,
        }),
        [],
    );

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

const useData = () => useContext(DataContext);

export { DataProvider, useData };
