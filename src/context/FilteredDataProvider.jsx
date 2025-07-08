import { createContext, useContext, useEffect, useMemo, useState } from 'react';

import data from '../recommender/data/entries.json';
import { returnFilteredData } from '../recommender/utils/filter';

const FilteredDataContext = createContext();

export const FilteredDataProvider = ({ children }) => {
    const [processedData, setProcessedData] = useState({
        filteredDemographics: [],
        filteredGenres: [],
        filteredLicensors: [],
        filteredProducers: [],
        filteredSeasons: [],
        filteredStudios: [],
        filteredThemes: [],
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
                filteredDemographics,
                filteredGenres,
                filteredLicensors,
                filteredProducers,
                filteredSeasons,
                filteredStudios,
                filteredThemes,
                processed: true,
            });
        };

        if (!processedData.processed) {
            processData();
        }
    }, [processedData]);

    const memoizedProcessedData = useMemo(() => processedData, [processedData]);

    return (
        <FilteredDataContext.Provider value={memoizedProcessedData}>
            {children}
        </FilteredDataContext.Provider>
    );
};

export const useFilteredData = () => useContext(FilteredDataContext);
