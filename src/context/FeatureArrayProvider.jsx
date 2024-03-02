import React, { createContext, useContext, useMemo, useRef } from 'react';

import featureArray from '../recommender/data/featureArray.json';

const FeatureArrayContext = createContext();

const FeatureArrayProvider = ({ children }) => {
    const featureArrayRef = useRef(featureArray);

    const state = useMemo(
        () => ({
            featureArray: featureArrayRef.current,
        }),
        [],
    );

    return <FeatureArrayContext.Provider value={state}>{children}</FeatureArrayContext.Provider>;
};

const useFeatureArray = () => useContext(FeatureArrayContext);

export { FeatureArrayProvider, useFeatureArray };
