import DataProvider from './DataProvider';
import FeatureArrayProvider from './FeatureArrayProvider';
import FilteredDataProvider from './FilteredDataProvider';
import KMeansProvider from './KMeansProvider';
import React from 'react';
import TitleIDMapProvider from './TitleIDMapProvider';
import TopAnimeProvider from './TopAnimeProvider';

const AppProvider = ({ children }) => {
    return (
        <DataProvider>
            <FeatureArrayProvider>
                <FilteredDataProvider>
                    <KMeansProvider>
                        <TitleIDMapProvider>
                            <TopAnimeProvider>{children}</TopAnimeProvider>
                        </TitleIDMapProvider>
                    </KMeansProvider>
                </FilteredDataProvider>
            </FeatureArrayProvider>
        </DataProvider>
    );
};

export default AppProvider;
