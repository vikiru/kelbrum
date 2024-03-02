import React, { createContext, useContext, useMemo, useRef } from 'react';

import kmeans from '../recommender/data/kmeans.json';

const KMeansContext = createContext();

export const KMeansProvider = ({ children }) => {
    const kmeansRef = useRef(kmeans);

    const state = useMemo(
        () => ({
            kmeans: kmeansRef.current,
        }),
        [],
    );

    return <KMeansContext.Provider value={state}>{children}</KMeansContext.Provider>;
};

export const useKMeans = () => useContext(KMeansContext);
