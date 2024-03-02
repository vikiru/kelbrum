import React, { createContext, useContext, useMemo } from 'react';

import featureArray from '../recommender/data/featureArray.json';

const FeatureArrayContext = createContext();

export const FeatureArrayProvider = ({ children }) => {
    const state = useMemo(() => ({
        featureArray: featureArray,
    }), []);

    return <FeatureArrayContext.Provider value={state}>{children}</FeatureArrayContext.Provider>;
};

export const useFeatureArray = () => useContext(FeatureArrayContext);
