import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import App from './App';
import { GlobalStyles } from './styles/GlobalStyles';
import './index.css';

const store = configureStore({
  reducer: {
    user: (await import('./slices/userSlice')).default,
    address: (await import('./slices/addressSlice')).default,
  },
});

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <GlobalStyles />
      <App />
    </Provider>
  </React.StrictMode>
);
