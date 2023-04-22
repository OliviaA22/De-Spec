import React from 'react';
import ReactDOM from 'react-dom';
import { ThemeProvider } from '@mui/material';
import theme from './components/theme';
import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter
import './index.css';
import App from './components/App';

ReactDOM.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}> {/* Wrap the App component with ThemeProvider */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
  document.getElementById('root')
);