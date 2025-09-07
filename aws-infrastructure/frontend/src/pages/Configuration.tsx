import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Divider,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Visibility,
  VisibilityOff,
  CheckCircle,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { saveApiKeys, getApiKeys, testApiConnection } from '../services/api';

interface ApiKeys {
  binanceApiKey: string;
  binanceApiSecret: string;
  bybitApiKey: string;
  bybitApiSecret: string;
  okxApiKey: string;
  okxApiSecret: string;
  okxPassphrase: string;
}

interface ConnectionStatus {
  binance: 'connected' | 'disconnected' | 'testing' | 'error';
  bybit: 'connected' | 'disconnected' | 'testing' | 'error';
  okx: 'connected' | 'disconnected' | 'testing' | 'error';
}

const Configuration: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    binanceApiKey: '',
    binanceApiSecret: '',
    bybitApiKey: '',
    bybitApiSecret: '',
    okxApiKey: '',
    okxApiSecret: '',
    okxPassphrase: '',
  });

  const [showSecrets, setShowSecrets] = useState<{[key: string]: boolean}>({});
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    binance: 'disconnected',
    bybit: 'disconnected',
    okx: 'disconnected',
  });
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{open: boolean, message: string, severity: 'success' | 'error'}>({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const keys = await getApiKeys();
      setApiKeys(keys);
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  const handleInputChange = (field: keyof ApiKeys) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setApiKeys(prev => ({
      ...prev,
      [field]: event.target.value
    }));
  };

  const toggleSecretVisibility = (field: string) => {
    setShowSecrets(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await saveApiKeys(apiKeys);
      setSnackbar({
        open: true,
        message: 'API keys saved successfully!',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to save API keys',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (exchange: keyof ConnectionStatus) => {
    setConnectionStatus(prev => ({ ...prev, [exchange]: 'testing' }));
    try {
      await testApiConnection(exchange, apiKeys);
      setConnectionStatus(prev => ({ ...prev, [exchange]: 'connected' }));
      setSnackbar({
        open: true,
        message: `${exchange} connection successful!`,
        severity: 'success'
      });
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, [exchange]: 'error' }));
      setSnackbar({
        open: true,
        message: `${exchange} connection failed`,
        severity: 'error'
      });
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case 'connected':
        return <Chip icon={<CheckCircle />} label="Connected" color="success" size="small" />;
      case 'testing':
        return <Chip label="Testing..." color="info" size="small" />;
      case 'error':
        return <Chip icon={<ErrorIcon />} label="Error" color="error" size="small" />;
      default:
        return <Chip label="Disconnected" color="default" size="small" />;
    }
  };

  const SecretField: React.FC<{
    label: string;
    value: string;
    field: keyof ApiKeys;
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  }> = ({ label, value, field, onChange }) => (
    <TextField
      fullWidth
      label={label}
      type={showSecrets[field] ? 'text' : 'password'}
      value={value}
      onChange={onChange}
      InputProps={{
        endAdornment: (
          <IconButton
            onClick={() => toggleSecretVisibility(field)}
            edge="end"
          >
            {showSecrets[field] ? <VisibilityOff /> : <Visibility />}
          </IconButton>
        ),
      }}
    />
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configuration
      </Typography>
      
      <Grid container spacing={3}>
        {/* API Keys Section */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  Exchange API Keys
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSave}
                  disabled={loading}
                >
                  Save All Keys
                </Button>
              </Box>

              <Grid container spacing={3}>
                {/* Binance */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">Binance</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusChip(connectionStatus.binance)}
                          <Tooltip title="Test Connection">
                            <IconButton
                              size="small"
                              onClick={() => testConnection('binance')}
                              disabled={connectionStatus.binance === 'testing'}
                            >
                              <RefreshIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      <SecretField
                        label="API Key"
                        value={apiKeys.binanceApiKey}
                        field="binanceApiKey"
                        onChange={handleInputChange('binanceApiKey')}
                      />
                      <Box sx={{ mt: 2 }}>
                        <SecretField
                          label="API Secret"
                          value={apiKeys.binanceApiSecret}
                          field="binanceApiSecret"
                          onChange={handleInputChange('binanceApiSecret')}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* Bybit */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">Bybit</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusChip(connectionStatus.bybit)}
                          <Tooltip title="Test Connection">
                            <IconButton
                              size="small"
                              onClick={() => testConnection('bybit')}
                              disabled={connectionStatus.bybit === 'testing'}
                            >
                              <RefreshIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      <SecretField
                        label="API Key"
                        value={apiKeys.bybitApiKey}
                        field="bybitApiKey"
                        onChange={handleInputChange('bybitApiKey')}
                      />
                      <Box sx={{ mt: 2 }}>
                        <SecretField
                          label="API Secret"
                          value={apiKeys.bybitApiSecret}
                          field="bybitApiSecret"
                          onChange={handleInputChange('bybitApiSecret')}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>

                {/* OKX */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h6">OKX</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusChip(connectionStatus.okx)}
                          <Tooltip title="Test Connection">
                            <IconButton
                              size="small"
                              onClick={() => testConnection('okx')}
                              disabled={connectionStatus.okx === 'testing'}
                            >
                              <RefreshIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </Box>
                      <SecretField
                        label="API Key"
                        value={apiKeys.okxApiKey}
                        field="okxApiKey"
                        onChange={handleInputChange('okxApiKey')}
                      />
                      <Box sx={{ mt: 2 }}>
                        <SecretField
                          label="API Secret"
                          value={apiKeys.okxApiSecret}
                          field="okxApiSecret"
                          onChange={handleInputChange('okxApiSecret')}
                        />
                      </Box>
                      <Box sx={{ mt: 2 }}>
                        <SecretField
                          label="Passphrase"
                          value={apiKeys.okxPassphrase}
                          field="okxPassphrase"
                          onChange={handleInputChange('okxPassphrase')}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Trading Parameters */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Trading Parameters
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Minimum Spread %"
                    type="number"
                    defaultValue="0.1"
                    inputProps={{ step: "0.01", min: "0" }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Maximum Position Size (USDT)"
                    type="number"
                    defaultValue="1000"
                    inputProps={{ min: "0" }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Enable Live Trading"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={<Switch />}
                    label="Paper Trading Mode"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* System Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Settings
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Log Level</InputLabel>
                    <Select
                      defaultValue="INFO"
                      label="Log Level"
                    >
                      <MenuItem value="DEBUG">DEBUG</MenuItem>
                      <MenuItem value="INFO">INFO</MenuItem>
                      <MenuItem value="WARNING">WARNING</MenuItem>
                      <MenuItem value="ERROR">ERROR</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Update Interval (seconds)"
                    type="number"
                    defaultValue="5"
                    inputProps={{ min: "1" }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Enable Notifications"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Configuration;
