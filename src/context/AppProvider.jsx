import React from 'react';

import { DataProvider } from './DataProvider';
import { FeatureArrayProvider } from './FeatureArrayProvider';
import { FilteredDataProvider } from './FilteredDataProvider';
import { KMeansProvider } from './KMeansProvider';
import { TitleIDMapProvider } from './TitleIDMapProvider';
import { TopAnimeProvider } from './TopAnimeProvider';

export const AppProvider = (Component) => {
    const CombineProviders = (props) => (
        <DataProvider>
            <FeatureArrayProvider>
                <FilteredDataProvider>
                    <KMeansProvider>
                        <TitleIDMapProvider>
                            <TopAnimeProvider>
                                <Component {...props} />
                            </TopAnimeProvider>
                        </TitleIDMapProvider>
                    </KMeansProvider>
                </FilteredDataProvider>
            </FeatureArrayProvider>
        </DataProvider>
    );
    return CombineProviders;
};
