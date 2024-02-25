import React from 'react';

import DataProvider from './context/DataProvider';
import Router from './pages/Router/Router';

function App() {
    return (
        <DataProvider>
            <Router />
        </DataProvider>
    );
}

export default App;
