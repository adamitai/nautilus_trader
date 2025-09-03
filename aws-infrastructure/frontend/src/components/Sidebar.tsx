import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as TradingIcon,
  AccountBalance as PortfolioIcon,
  Analytics as AnalyticsIcon,
  Settings as SystemIcon,
  Tune as ConfigIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const drawerWidth = 240;

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Trading', icon: <TradingIcon />, path: '/trading' },
  { text: 'Portfolio', icon: <PortfolioIcon />, path: '/portfolio' },
  { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  { text: 'System', icon: <SystemIcon />, path: '/system' },
  { text: 'Configuration', icon: <ConfigIcon />, path: '/configuration' },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
    onClose();
  };

  const drawer = (
    <Box>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
          Trading System
        </Typography>
        <Typography variant="caption" color="text.secondary">
          v1.0.0
        </Typography>
      </Box>
      
      <Divider />
      
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: location.pathname === item.path ? 'white' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                sx={{ color: location.pathname === item.path ? 'white' : 'inherit' }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider sx={{ mt: 'auto' }} />
      
      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block">
          System Status
        </Typography>
        <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>
          ● Online
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          top: 64, // Height of AppBar
        },
      }}
    >
      {drawer}
    </Drawer>
  );
};

export default Sidebar;
