import React, { createContext, useContext, useEffect, useReducer } from 'react';

import data from '../../../reccomender/data/entries';
import featureArray from '../../../reccomender/data/featureArray';
import kmeans from '../../../reccomender/data/kmeans';
import titleIDMap from '../../../reccomender/data/titleIDMap';

const DataContext = createContext();

export const DataProvider = ({ children }) => {
    const [state, dispatch] = useReducer(
        (state, action) => {
            switch (action.type) {
                case 'INITIALIZE_DATA':
                    return {
                        ...state,
                        data: action.payload.data,
                        featureArray: action.payload.featureArray,
                        kmeans: action.payload.kmeans,
                        titleIDMap: action.payload.titleIDMap,
                    };
                default:
                    return state;
            }
        },
        { data: [], featureArray: [], kmeans: [], titleIDMap: [] },
    );

    useEffect(() => {
        const initialize = async () => {
            dispatch({ type: 'INITIALIZE_DATA', payload: { data, featureArray, kmeans, titleIDMap } });
        };

        initialize();
    }, []);

    return <DataContext.Provider value={{ ...state }}>{children}</DataContext.Provider>;
};

export const useData = () => useContext(DataContext);

export default DataProvider;
