import React, { createContext, useContext, useMemo, useRef } from 'react';

import featureArray from '../recommender/data/featureArray.json';

const FeatureArrayContext = createContext();

export const FeatureArrayProvider = ({ children }) => {
    const featureArrayRef = useRef(featureArray);

    const state = useMemo(
        () => ({
            featureArray: featureArrayRef.current,
        }),
        [],
    );

    return <FeatureArrayContext.Provider value={state}>{children}</FeatureArrayContext.Provider>;
};

export const useFeatureArray = () => useContext(FeatureArrayContext);

