import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import data from '../recommender/data/entries.json';
import { returnFilteredData } from '../recommender/utils/filter';

const FilteredDataContext = createContext();

export const FilteredDataProvider = ({ children }) => {
    const [processedData, setProcessedData] = useState({
        filteredGenres: [],
        filteredThemes: [],
        filteredDemographics: [],
        filteredProducers: [],
        filteredStudios: [],
        filteredLicensors: [],
        filteredSeasons: [],
        processed: false,
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
                processed: true,
            });
        };

        if (!processedData.processed) {
            processData();
        }
    }, [data, processedData]);

    const memoizedProcessedData = useMemo(() => processedData, [processedData]);

    return <FilteredDataContext.Provider value={memoizedProcessedData}>{children}</FilteredDataContext.Provider>;
};

export const useFilteredData = () => useContext(FilteredDataContext);
