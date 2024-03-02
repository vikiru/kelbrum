import React, { createContext, useContext, useMemo, useRef } from 'react';

import data from '../recommender/data/entries.json';
import { returnFilteredData } from '../recommender/utils/filter';

const FilteredDataContext = createContext();

const FilteredDataProvider = ({ children }) => {
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

            processedData = {
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

        if (!processedData.current.processed) {
            processData();
        }
    }, []);

    const state = useMemo(
        () => ({
            ...processedDataRef.current,
        }),
        [],
    );

    return <FilteredDataContext.Provider value={state}>{children}</FilteredDataContext.Provider>;
};

const useFilteredData = () => useContext(FilteredDataContext);

export { FilteredDataProvider, useFilteredData };
