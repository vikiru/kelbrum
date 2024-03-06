import React from 'react';

import { AppProvider } from './context/AppProvider';
import Router from './pages/Router/Router';

function App() {
    return <Router />;
}

export default AppProvider(App);
