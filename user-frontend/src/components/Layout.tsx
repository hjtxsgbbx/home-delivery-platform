import React from 'react';
import { Outlet } from 'react-router-dom';

interface LayoutProps {}

const Layout: React.FC<LayoutProps> = () => {
  return (
    <div className="app-layout">
      <header className="header">
        <h1>家政服务平台</h1>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
