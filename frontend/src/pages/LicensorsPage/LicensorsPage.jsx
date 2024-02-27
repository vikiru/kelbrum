import React, { useEffect, useMemo, useState } from 'react';

import DataList from './../../components/DataList/DataList';
import { useData } from '../../context/DataProvider';

function LicensorsPage() {
    const { filteredLicensors } = useData();

    return (
        <div className="min-h-screen bg-secondary pb-16">
            <DataList title="Licensors" data={filteredLicensors} path="licensors" />
        </div>
    );
}

export default React.memo(LicensorsPage);
