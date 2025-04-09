// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import BasicTable from './pages/BasicTable';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<BasicTable />} />
      </Routes>
    </Router>
  );
};

export default App;
