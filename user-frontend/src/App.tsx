import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ServiceListPage from './pages/ServiceListPage';
import ServiceDetailPage from './pages/ServiceDetailPage';
import OrderConfirmPage from './pages/OrderConfirmPage';
import PersonalCenterPage from './pages/PersonalCenterPage';
import AddressManagementPage from './pages/AddressManagementPage';
import { GlobalStyles } from './styles/GlobalStyles';

const App: React.FC = () => {
  return (
    <Router>
      <GlobalStyles />
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/services" element={<ServiceListPage />} />
          <Route path="/services/:id" element={<ServiceDetailPage />} />
          <Route path="/order/confirm" element={<OrderConfirmPage />} />
          <Route path="/personal-center" element={<PersonalCenterPage />} />
          <Route path="/addresses" element={<AddressManagementPage />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
