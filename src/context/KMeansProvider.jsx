import React, { createContext, useContext, useMemo } from 'react';

import kmeans from '../recommender/data/kmeans.json';

const KMeansContext = createContext();

export const KMeansProvider = ({ children }) => {
    const state = useMemo(() => ({
        kmeans: kmeans,
    }), []);

    return <KMeansContext.Provider value={state}>{children}</KMeansContext.Provider>;
};

export const useKMeans = () => useContext(KMeansContext);
