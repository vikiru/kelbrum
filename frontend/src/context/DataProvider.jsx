import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import data from '../../../reccomender/data/entries.json';
import featureArray from '../../../reccomender/data/featureArray.json';
import kmeans from '../../../reccomender/data/kmeans.json';
import titleIDMap from '../../../reccomender/data/titleIDMap.json';
import { returnFilteredData } from '../../../reccomender/utils/utils';

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
            const filteredGenres = await returnFilteredData(data, 'genres');
            const filteredThemes = await returnFilteredData(data, 'themes');
            const filteredDemographics = await returnFilteredData(data, 'demographics');
            const filteredProducers = await returnFilteredData(data, 'producers');
            const filteredStudios = await returnFilteredData(data, 'studios');
            const filteredLicensors = await returnFilteredData(data, 'licensors');
            const filteredSeasons = await returnFilteredData(data, 'premiered');

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
