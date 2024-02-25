import React, { createContext, useContext, useMemo, useState } from 'react';

import data from '../../../reccomender/data/entries.json';
import featureArray from '../../../reccomender/data/featureArray.json';
import kmeans from '../../../reccomender/data/kmeans.json';
import titleIDMap from '../../../reccomender/data/titleIDMap.json';

const DataContext = createContext();

export const DataProvider = ({ children }) => {
    const initialState = useMemo(
        () => ({
            data: data,
            featureArray: featureArray,
            kmeans: kmeans,
            titleIDMap: titleIDMap,
        }),
        [],
    );

    const [state, setState] = useState(initialState);

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

export const useData = () => useContext(DataContext);

export default DataProvider;
