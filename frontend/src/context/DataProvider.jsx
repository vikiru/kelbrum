import React, { createContext, useContext, useEffect, useState } from 'react';

import data from '../../../reccomender/data/entries.json';
import featureArray from '../../../reccomender/data/featureArray.json';
import kmeans from '../../../reccomender/data/kmeans.json';
import titleIDMap from '../../../reccomender/data/titleIDMap.json';
import { createMapping } from '../../../reccomender/utils/stats';
import { returnFilteredData, returnUniqueArray } from '../../../reccomender/utils/utils';

const DataContext = createContext();

export const DataProvider = ({ children }) => {
    const [processedData, setProcessedData] = useState({ filteredGenres: [], filteredDemographics: [] });

    useEffect(() => {
        const processData = async () => {
            const filteredGenres = await returnFilteredData(data, 'genres');
            const filteredDemographics = await returnFilteredData(data, 'demographics');
            const filteredProducers = await returnFilteredData(data, 'producers');
            const filteredStudios = await returnFilteredData(data, 'studios');
            const filteredLicensors = await returnFilteredData(data, 'licensors');
            const filteredSeasons = await returnFilteredData(data, 'premiered');

            setProcessedData({
                filteredGenres,
                filteredDemographics,
                filteredProducers,
                filteredStudios,
                filteredLicensors,
                filteredSeasons,
            });
        };

        processData();
    }, [data]);

    const state = {
        ...processedData,
        data: data,
        featureArray: featureArray,
        kmeans: kmeans,
        titleIDMap: titleIDMap,
    };

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

export const useData = () => useContext(DataContext);

export default DataProvider;
