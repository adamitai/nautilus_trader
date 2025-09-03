import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Trading from './pages/Trading';
import Portfolio from './pages/Portfolio';
import Analytics from './pages/Analytics';
import System from './pages/System';
import Configuration from './pages/Configuration';

// Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#1a1a1a',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1a1a1a',
        },
      },
    },
  },
});

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          <Navbar onMenuClick={handleSidebarToggle} />
          <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              width: { sm: `calc(100% - ${sidebarOpen ? 240 : 0}px)` },
              ml: { sm: sidebarOpen ? '240px' : 0 },
              transition: 'margin 0.3s ease',
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/trading" element={<Trading />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/system" element={<System />} />
              <Route path="/configuration" element={<Configuration />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;
