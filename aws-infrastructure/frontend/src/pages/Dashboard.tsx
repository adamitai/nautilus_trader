import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Speed,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data - replace with real API calls
const mockData = {
  opportunities: [
    { symbol: 'BTCUSDT', exchange1: 'Binance', exchange2: 'Bybit', spread: 0.45, profit: 125.50, timestamp: '2024-01-15 10:30:00' },
    { symbol: 'ETHUSDT', exchange1: 'OKX', exchange2: 'Binance', spread: 0.32, profit: 89.25, timestamp: '2024-01-15 10:29:45' },
    { symbol: 'ADAUSDT', exchange1: 'Bybit', exchange2: 'OKX', spread: 0.28, profit: 45.80, timestamp: '2024-01-15 10:29:30' },
  ],
  performance: [
    { time: '10:00', pnl: 120 },
    { time: '10:05', pnl: 135 },
    { time: '10:10', pnl: 142 },
    { time: '10:15', pnl: 138 },
    { time: '10:20', pnl: 155 },
    { time: '10:25', pnl: 168 },
    { time: '10:30', pnl: 175 },
  ],
  stats: {
    totalPnl: 175.50,
    todayTrades: 12,
    successRate: 94.2,
    activeOpportunities: 3,
  },
  exchanges: [
    { name: 'Binance', status: 'online', latency: 45 },
    { name: 'Bybit', status: 'online', latency: 52 },
    { name: 'OKX', status: 'online', latency: 38 },
  ],
};

const Dashboard: React.FC = () => {
  const [data, setData] = useState(mockData);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      // In a real app, this would fetch data from your API
      setData(prevData => ({
        ...prevData,
        stats: {
          ...prevData.stats,
          totalPnl: prevData.stats.totalPnl + (Math.random() - 0.5) * 10,
        },
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
    trend?: number;
  }> = ({ title, value, icon, color, trend }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="h6">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ color }}>
              {typeof value === 'number' ? value.toFixed(2) : value}
            </Typography>
            {trend !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {trend > 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
                <Typography variant="body2" color={trend > 0 ? 'success.main' : 'error.main'}>
                  {Math.abs(trend).toFixed(1)}%
                </Typography>
              </Box>
            )}
          </Box>
          <Box sx={{ color, opacity: 0.7 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h4" gutterBottom>
        Trading Dashboard
      </Typography>
      
      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total P&L"
            value={`$${data.stats.totalPnl}`}
            icon={<AccountBalance />}
            color="primary.main"
            trend={2.3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Trades"
            value={data.stats.todayTrades}
            icon={<Speed />}
            color="info.main"
            trend={15.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Success Rate"
            value={`${data.stats.successRate}%`}
            icon={<CheckCircle />}
            color="success.main"
            trend={1.8}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Opportunities"
            value={data.stats.activeOpportunities}
            icon={<TrendingUp />}
            color="warning.main"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* P&L Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                P&L Performance
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data.performance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="pnl" stroke="#1976d2" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Exchange Status */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Exchange Status
              </Typography>
              {data.exchanges.map((exchange) => (
                <Box key={exchange.name} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1">{exchange.name}</Typography>
                    <Chip
                      label={exchange.status}
                      color={exchange.status === 'online' ? 'success' : 'error'}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Latency: {exchange.latency}ms
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={Math.max(0, 100 - exchange.latency)}
                      sx={{ ml: 1, width: 60, height: 4 }}
                    />
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Opportunities */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Arbitrage Opportunities
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell>Exchanges</TableCell>
                      <TableCell align="right">Spread %</TableCell>
                      <TableCell align="right">Profit</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.opportunities.map((opp, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                            {opp.symbol}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {opp.exchange1} → {opp.exchange2}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1" color="success.main">
                            {opp.spread}%
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1" color="success.main">
                            ${opp.profit}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {opp.timestamp}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label="Active"
                            color="success"
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
