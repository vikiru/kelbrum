import React, { createContext, useContext, useMemo, useRef } from 'react';

import kmeans from '../recommender/data/kmeans.json';

const KMeansContext = createContext();

const KMeansProvider = ({ children }) => {
    const kmeansRef = useRef(kmeans);

    const state = useMemo(
        () => ({
            kmeans: kmeansRef.current,
        }),
        [],
    );

    return <KMeansContext.Provider value={state}>{children}</KMeansContext.Provider>;
};

const useKMeans = () => useContext(KMeansContext);

export { KMeansProvider, useKMeans };
