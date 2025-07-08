import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import DataList from './../../components/DataList/DataList';
import { useFilteredData } from '../../context/FilteredDataProvider';

function LicensorsPage() {
    const { filteredLicensors } = useFilteredData();
    const location = useLocation();
    const isLicensorDetailPage = location.pathname === '/anime/licensors';
    return (
        <section
            className="min-h-screen bg-secondary pb-16 dark:bg-gray-900"
            id="licensors"
        >
            {isLicensorDetailPage && (
                <DataList
                    data={filteredLicensors}
                    path="licensors"
                    title="Licensors"
                />
            )}
            <Outlet />
        </section>
    );
}

export default React.memo(LicensorsPage);
