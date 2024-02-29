import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import data from '../../../reccomender/data/entries.json';
import featureArray from '../../../reccomender/data/featureArray.json';
import kmeans from '../../../reccomender/data/kmeans.json';
import titleIDMap from '../../../reccomender/data/titleIDMap.json';
import { returnFilteredData } from '../../../reccomender/utils/filter';

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
    }, [data]);

    const state = useMemo(
        () => ({
            ...processedData,
            data: data,
            featureArray: featureArray,
            kmeans: kmeans,
            titleIDMap: titleIDMap,
        }),
        [processedData, data, featureArray, kmeans, titleIDMap],
    );

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

const useData = () => useContext(DataContext);

export { DataProvider, useData };
