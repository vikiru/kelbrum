import React, { createContext, useContext, useEffect, useMemo, useRef } from 'react';

import data from '../recommender/data/entries.json';
import { returnFilteredData } from '../recommender/utils/filter';

const FilteredDataContext = createContext();

export const FilteredDataProvider = ({ children }) => {
    const processedDataRef = useRef({
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

            processedDataRef.current = {
                filteredGenres,
                filteredThemes,
                filteredDemographics,
                filteredProducers,
                filteredStudios,
                filteredLicensors,
                filteredSeasons,
                processed: true,
            };
        };

        processData();
    }, []);

    return <FilteredDataContext.Provider value={processedDataRef.current}>{children}</FilteredDataContext.Provider>;
};

export const useFilteredData = () => useContext(FilteredDataContext);
