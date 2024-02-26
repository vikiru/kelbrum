import React, { useEffect, useMemo, useState } from 'react';

import { useData } from '../../context/DataProvider';
import DataList from './../../components/DataList/DataList';

function LicensorsPage() {
    const { filteredLicensors } = useData();

    return (
        <div className="min-h-screen bg-secondary pb-16">
            <DataList title="Licensors" data={filteredLicensors} path="licensors" />
        </div>
    );
}

export default LicensorsPage;
