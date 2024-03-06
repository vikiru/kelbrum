import React, { useEffect, useMemo, useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { useFilteredData } from '../../context/FilteredDataProvider';
import DataList from './../../components/DataList/DataList';

function LicensorsPage() {
    const { filteredLicensors } = useFilteredData();
    const location = useLocation();
    const isLicensorDetailPage = location.pathname === '/anime/licensors';
    return (
        <section id="licensors" className="min-h-screen bg-secondary pb-16 dark:bg-gray-900">
            {isLicensorDetailPage && <DataList title="Licensors" data={filteredLicensors} path="licensors" />}
            <Outlet />
        </section>
    );
}

export default React.memo(LicensorsPage);
