import { DataProvider } from './context/DataProvider';
import React from 'react';
import Router from './pages/Router/Router';

function App() {
    return (
        <DataProvider>
            <Router />
        </DataProvider>
    );
}

export { App };
