import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import data from '../../../recommender/data/entries.json';
import featureArray from '../../../recommender/data/featureArray.json';
import kmeans from '../../../recommender/data/kmeans.json';
import titleIDMap from '../../../recommender/data/titleIDMap.json';
import { returnFilteredData } from '../../../recommender/utils/filter';

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const [processedData, setProcessedData] = useState({
        filteredGenres: [],
        filteredThemes: [],
        filteredDemographics: [],
        filteredProducers: [],
        filteredStudios: [],
        filteredLicensors: [],
        filteredSeasons: [],
    });

    useEffect(() => {
        const processData = async () => {
            const promises = [
                returnFilteredData(data, 'genres'),
                returnFilteredData(data, 'themes'),
                returnFilteredData(data, 'demographics'),
                returnFilteredData(data, 'producers'),
                returnFilteredData(data, 'studios'),
                returnFilteredData(data, 'licensors'),
                returnFilteredData(data, 'premiered'),
            ];

            const [
                filteredGenres,
                filteredThemes,
                filteredDemographics,
                filteredProducers,
                filteredStudios,
                filteredLicensors,
                filteredSeasons,
            ] = await Promise.all(promises);

            setProcessedData({
                filteredGenres,
                filteredThemes,
                filteredDemographics,
                filteredProducers,
                filteredStudios,
                filteredLicensors,
                filteredSeasons,
            });
        };

        processData();
    }, []);

    const state = useMemo(
        () => ({
            ...processedData,
            data: data,
            featureArray: featureArray,
            kmeans: kmeans,
            titleIDMap: titleIDMap,
        }),
        [processedData],
    );

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

const useData = () => useContext(DataContext);

export { DataProvider, useData };
