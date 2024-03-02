import React, { createContext, useContext, useEffect, useMemo, useRef } from 'react';

import data from '../recommender/data/entries.json';
import featureArray from '../recommender/data/featureArray.json';
import kmeans from '../recommender/data/kmeans.json';
import { returnFilteredData } from '../recommender/utils/filter';
import titleIDMap from '../recommender/data/titleIDMap.json';

const DataContext = createContext();

const DataProvider = ({ children }) => {
    const processedDataRef = useRef({
        filteredGenres: [],
        filteredThemes: [],
        filteredDemographics: [],
        filteredProducers: [],
        filteredStudios: [],
        filteredLicensors: [],
        filteredSeasons: [],
        processed: false
    });

    const dataRef = useRef(data);
    const featureArrayRef = useRef(featureArray);
    const kmeansRef = useRef(kmeans);
    const titleIDMapRef = useRef(titleIDMap);
    const topAnime = [...dataRef.current].sort((a, b) => b.score - a.score).slice(0, 100);
    const topAnimeRef = useRef(topAnime);

    useEffect(() => {
        const processData = async () => {
            const promises = [
                returnFilteredData(dataRef.current, 'genres'),
                returnFilteredData(dataRef.current, 'themes'),
                returnFilteredData(dataRef.current, 'demographics'),
                returnFilteredData(dataRef.current, 'producers'),
                returnFilteredData(dataRef.current, 'studios'),
                returnFilteredData(dataRef.current, 'licensors'),
                returnFilteredData(dataRef.current, 'premiered'),
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

        if (!processedDataRef.current.processed) {
            processData();
        }
    }, []);

    const state = useMemo(
        () => ({
            ...processedDataRef.current,
            data: dataRef.current,
            featureArray: featureArrayRef.current,
            kmeans: kmeansRef.current,
            titleIDMap: titleIDMapRef.current,
            topAnime: topAnimeRef.current
        }),
        [],
    );

    return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
};

const useData = () => useContext(DataContext);

export { DataProvider, useData };
