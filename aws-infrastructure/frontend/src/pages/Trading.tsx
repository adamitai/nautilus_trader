import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Refresh,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';

// Mock data for trading opportunities
const mockOpportunities = [
  {
    id: 1,
    symbol: 'BTCUSDT',
    buyExchange: 'Binance',
    sellExchange: 'Bybit',
    buyPrice: 43250.50,
    sellPrice: 43445.25,
    spread: 0.45,
    volume: 1000,
    profit: 194.75,
    confidence: 95,
    status: 'active',
    timestamp: new Date(),
  },
  {
    id: 2,
    symbol: 'ETHUSDT',
    buyExchange: 'OKX',
    sellExchange: 'Binance',
    buyPrice: 2650.30,
    sellPrice: 2658.75,
    spread: 0.32,
    volume: 500,
    profit: 42.25,
    confidence: 88,
    status: 'active',
    timestamp: new Date(),
  },
  {
    id: 3,
    symbol: 'ADAUSDT',
    buyExchange: 'Bybit',
    sellExchange: 'OKX',
    buyPrice: 0.4850,
    sellPrice: 0.4864,
    spread: 0.29,
    volume: 2000,
    profit: 28.80,
    confidence: 82,
    status: 'executed',
    timestamp: new Date(),
  },
];

const Trading: React.FC = () => {
  const [opportunities, setOpportunities] = useState(mockOpportunities);
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isMonitoring) {
      interval = setInterval(() => {
        // Simulate real-time updates
        setOpportunities(prev => 
          prev.map(opp => ({
            ...opp,
            buyPrice: opp.buyPrice + (Math.random() - 0.5) * 10,
            sellPrice: opp.sellPrice + (Math.random() - 0.5) * 10,
            spread: Math.abs(opp.sellPrice - opp.buyPrice) / opp.buyPrice * 100,
            profit: Math.abs(opp.sellPrice - opp.buyPrice) * opp.volume,
            timestamp: new Date(),
          }))
        );
        setLastUpdate(new Date());
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isMonitoring]);

  const handleExecuteTrade = (opportunityId: number) => {
    setOpportunities(prev =>
      prev.map(opp =>
        opp.id === opportunityId
          ? { ...opp, status: 'executing' }
          : opp
      )
    );

    // Simulate trade execution
    setTimeout(() => {
      setOpportunities(prev =>
        prev.map(opp =>
          opp.id === opportunityId
            ? { ...opp, status: 'executed' }
            : opp
        )
      );
    }, 3000);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'executing': return 'warning';
      case 'executed': return 'info';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle />;
      case 'executing': return <LinearProgress />;
      case 'executed': return <CheckCircle />;
      case 'failed': return <Error />;
      default: return null;
    }
  };

  return (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Trading Monitor
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => setLastUpdate(new Date())}
          >
            Refresh
          </Button>
          <Button
            variant={isMonitoring ? 'contained' : 'outlined'}
            startIcon={isMonitoring ? <Pause /> : <PlayArrow />}
            onClick={() => setIsMonitoring(!isMonitoring)}
            color={isMonitoring ? 'error' : 'success'}
          >
            {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
          </Button>
        </Box>
      </Box>

      {/* Status Alert */}
      <Alert 
        severity={isMonitoring ? 'success' : 'warning'} 
        sx={{ mb: 3 }}
        action={
          <Typography variant="body2" color="text.secondary">
            Last update: {lastUpdate.toLocaleTimeString()}
          </Typography>
        }
      >
        {isMonitoring 
          ? 'Live monitoring active - Real-time arbitrage detection running'
          : 'Monitoring paused - No new opportunities will be detected'
        }
      </Alert>

      {/* Trading Opportunities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Arbitrage Opportunities
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell>Buy Exchange</TableCell>
                  <TableCell>Buy Price</TableCell>
                  <TableCell>Sell Exchange</TableCell>
                  <TableCell>Sell Price</TableCell>
                  <TableCell align="right">Spread %</TableCell>
                  <TableCell align="right">Volume</TableCell>
                  <TableCell align="right">Profit</TableCell>
                  <TableCell align="center">Confidence</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="center">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {opportunities.map((opp) => (
                  <TableRow key={opp.id}>
                    <TableCell>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        {opp.symbol}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={opp.buyExchange} size="small" color="primary" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        ${opp.buyPrice.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={opp.sellExchange} size="small" color="secondary" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        ${opp.sellPrice.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        <TrendingUp color="success" sx={{ mr: 0.5 }} />
                        <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>
                          {opp.spread.toFixed(2)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {opp.volume}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>
                        ${opp.profit.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <LinearProgress
                          variant="determinate"
                          value={opp.confidence}
                          sx={{ width: 60, mr: 1 }}
                        />
                        <Typography variant="body2">
                          {opp.confidence}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={opp.status}
                        color={getStatusColor(opp.status) as any}
                        size="small"
                        icon={getStatusIcon(opp.status)}
                      />
                    </TableCell>
                    <TableCell align="center">
                      {opp.status === 'active' && (
                        <Button
                          variant="contained"
                          size="small"
                          color="success"
                          onClick={() => handleExecuteTrade(opp.id)}
                        >
                          Execute
                        </Button>
                      )}
                      {opp.status === 'executing' && (
                        <Tooltip title="Trade executing...">
                          <IconButton disabled>
                            <LinearProgress />
                          </IconButton>
                        </Tooltip>
                      )}
                      {opp.status === 'executed' && (
                        <Chip
                          label="Completed"
                          color="success"
                          size="small"
                        />
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Trading Statistics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Today's Performance
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Total Trades:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>12</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Successful:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>11</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Failed:</Typography>
                <Typography variant="body2" color="error.main" sx={{ fontWeight: 'bold' }}>1</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Success Rate:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>91.7%</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profit & Loss
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Total P&L:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>+$1,247.50</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Best Trade:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>+$194.75</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Worst Trade:</Typography>
                <Typography variant="body2" color="error.main" sx={{ fontWeight: 'bold' }}>-$23.40</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Avg Profit:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>+$103.96</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Risk Metrics
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Max Drawdown:</Typography>
                <Typography variant="body2" color="warning.main" sx={{ fontWeight: 'bold' }}>-2.3%</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Sharpe Ratio:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>2.47</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Volatility:</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>12.5%</Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                <Typography variant="body2">Risk Score:</Typography>
                <Typography variant="body2" color="success.main" sx={{ fontWeight: 'bold' }}>Low</Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Trading;
