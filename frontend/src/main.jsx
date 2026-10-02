import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, useLocation, useNavigate } from 'react-router-dom';
import api from './api';
import {
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  Bell,
  ChevronDown,
  CircleHelp,
  CreditCard,
  LayoutDashboard,
  Menu,
  MoreHorizontal,
  Plus,
  Search,
  Settings,
  Sparkles,
  Target,
  TrendingUp,
  Wallet,
  X,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import './styles.css';

const COLORS = ['#d95d39', '#2f6f68', '#e7a83f', '#6574a8', '#a85b78', '#6a8f62', '#9a7654'];
const currency = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });
const compactCurrency = new Intl.NumberFormat('en-IN', { notation: 'compact', maximumFractionDigits: 1 });

function App() {
  const [transactions, setTransactions] = useState([]);
  const [query, setQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [dateRange, setDateRange] = useState('Last 6 months');
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const activeView = viewFromPath(location.pathname);

  useEffect(() => {
    api.get('/transactions')
      .then((transactionResponse) => transactionResponse.data.map((row) => ({
        ...row,
        amount: Number(row.amount),
        date: new Date(row.date),
      })))
      .then(setTransactions)
      .catch(() => setTransactions([]))
      .finally(() => setLoading(false));
  }, []);

  const filteredTransactions = useMemo(() => {
    const cutoff = new Date();
    cutoff.setMonth(cutoff.getMonth() - (dateRange === 'Last 6 months' ? 6 : 12));
    return transactions.filter((transaction) => {
      const matchesDate = transaction.date >= cutoff;
      const search = query.toLowerCase();
      const matchesQuery = !search || [transaction.description, transaction.category, transaction.merchant]
        .join(' ').toLowerCase().includes(search);
      return matchesDate && matchesQuery;
    });
  }, [transactions, query, dateRange]);

  const metrics = useMemo(() => {
    const income = filteredTransactions.filter((item) => item.type === 'Income').reduce((sum, item) => sum + item.amount, 0);
    const expenses = filteredTransactions.filter((item) => item.type === 'Expense').reduce((sum, item) => sum + item.amount, 0);
    return { income, expenses, savings: income - expenses, rate: income ? ((income - expenses) / income) * 100 : 0 };
  }, [filteredTransactions]);

  const monthlyData = useMemo(() => {
    const months = new Map();
    filteredTransactions.forEach((item) => {
      const key = item.date.toLocaleDateString('en-US', { month: 'short' });
      if (!months.has(key)) months.set(key, { month: key, income: 0, expenses: 0, sort: item.date.getMonth() });
      months.get(key)[item.type === 'Income' ? 'income' : 'expenses'] += item.amount;
    });
    return [...months.values()].sort((a, b) => a.sort - b.sort);
  }, [filteredTransactions]);

  const categoryData = useMemo(() => {
    const categories = new Map();
    filteredTransactions.filter((item) => item.type === 'Expense').forEach((item) => {
      categories.set(item.category, (categories.get(item.category) || 0) + item.amount);
    });
    return [...categories.entries()].map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value).slice(0, 7);
  }, [filteredTransactions]);

  const recentTransactions = [...filteredTransactions].sort((a, b) => b.date - a.date).slice(0, 6);
  const navItems = [
    { label: 'Overview', icon: LayoutDashboard },
    { label: 'Transactions', icon: CreditCard },
    { label: 'Expense Analysis', icon: BarChart3 },
    { label: 'Budget', icon: Target },
    { label: 'Monthly Summary', icon: TrendingUp },
    { label: 'Insights', icon: Sparkles },
    { label: 'Import Data', icon: Plus },
  ];

  return (
    <div className="app-shell">
      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="brand"><span className="brand-mark">F</span><span>finsight</span></div>
        <div className="workspace-switcher"><span className="avatar">YV</span><span><strong>Yash&apos;s workspace</strong><small>Personal account</small></span><ChevronDown size={15} /></div>
        <nav className="main-nav" aria-label="Main navigation">
          <p className="eyebrow">Workspace</p>
          {navItems.map(({ label, icon: Icon }) => <button key={label} className={`nav-item ${activeView === label ? 'active' : ''}`} onClick={() => { navigate(pathForView(label)); setMenuOpen(false); }}><Icon size={18} /><span>{label}</span>{label === 'Insights' && <span className="nav-dot" />}</button>)}
          <p className="eyebrow nav-spacer">Manage</p>
          <button className={`nav-item ${activeView === 'Settings' ? 'active' : ''}`} onClick={() => navigate('/settings')}><Settings size={18} /><span>Settings</span></button>
        </nav>
        <div className="sidebar-footer"><div className="help-card"><CircleHelp size={18} /><div><strong>Need a hand?</strong><span>Read our quick guide</span></div><ArrowUpRight size={15} /></div><span className="version">Finsight v1.0 · Educational use</span></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><button className="icon-button mobile-menu" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">{menuOpen ? <X size={20} /> : <Menu size={20} />}</button><div className="breadcrumb"><span>Workspace</span><span>/</span><strong>{activeView}</strong></div><div className="top-actions"><button className="icon-button" aria-label="Notifications"><Bell size={19} /><i /></button><div className="top-avatar">YV</div></div></header>

        <div className="content-wrap">
          <div className="page-heading"><div><p className="kicker">{new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date())}</p><h1>Good morning, Yash<span className="accent">.</span></h1><p className="subheading">Here&apos;s what&apos;s happening with your money.</p></div><button className="primary-button"><Plus size={17} /> Add transaction</button></div>
          <div className="toolbar"><div className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search transactions" /></div><select value={dateRange} onChange={(event) => setDateRange(event.target.value)} aria-label="Date range"><option>Last 6 months</option><option>Last 12 months</option></select><button className="icon-button"><MoreHorizontal size={19} /></button></div>

          {loading ? <div className="loading-state">Loading your financial picture...</div> : activeView === 'Overview' ? <>
            <section className="metric-grid" aria-label="Financial summary">
              <MetricCard label="Total balance" value={metrics.savings} delta="12.8%" detail="vs. previous period" icon={Wallet} tone="dark" />
              <MetricCard label="Income" value={metrics.income} delta="8.4%" detail="vs. previous period" icon={ArrowDownRight} tone="green" />
              <MetricCard label="Expenses" value={metrics.expenses} delta="3.2%" detail="vs. previous period" icon={ArrowUpRight} tone="orange" negative />
              <div className="metric-card savings-card"><div className="metric-icon"><TrendingUp size={18} /></div><span className="metric-label">Savings rate</span><strong className="metric-value">{metrics.rate.toFixed(1)}%</strong><div className="progress-track"><span style={{ width: `${Math.min(metrics.rate, 100)}%` }} /></div><span className="metric-detail">Target: 20% <b>On track</b></span></div>
            </section>

            <section className="chart-grid"><div className="panel trend-panel"><PanelHeading title="Cash flow" subtitle="Income and expenses over time" action={<select value={dateRange} onChange={(event) => setDateRange(event.target.value)}><option>Last 6 months</option><option>Last 12 months</option></select>} /><div className="chart-legend"><span><i className="legend-income" />Income</span><span><i className="legend-expenses" />Expenses</span></div><div className="chart-area"><ResponsiveContainer width="100%" height="100%"><AreaChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}><defs><linearGradient id="incomeFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2f6f68" stopOpacity={0.2} /><stop offset="100%" stopColor="#2f6f68" stopOpacity={0} /></linearGradient><linearGradient id="expenseFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#d95d39" stopOpacity={0.14} /><stop offset="100%" stopColor="#d95d39" stopOpacity={0} /></linearGradient></defs><CartesianGrid vertical={false} stroke="#e9e9e3" /><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#8b918b', fontSize: 12 }} /><YAxis axisLine={false} tickLine={false} tick={{ fill: '#8b918b', fontSize: 11 }} tickFormatter={(value) => `₹${compactCurrency.format(value)}`} /><Tooltip formatter={(value) => currency.format(value)} contentStyle={{ border: '1px solid #e5e6df', borderRadius: 8, boxShadow: '0 8px 20px #26352a14' }} /><Area type="monotone" dataKey="income" stroke="#2f6f68" strokeWidth={2.5} fill="url(#incomeFill)" /><Area type="monotone" dataKey="expenses" stroke="#d95d39" strokeWidth={2.5} fill="url(#expenseFill)" /></AreaChart></ResponsiveContainer></div></div><div className="panel category-panel"><PanelHeading title="Where your money goes" subtitle="Spending by category" action={<button className="text-button">View details <ArrowUpRight size={14} /></button>} /><div className="donut-wrap"><ResponsiveContainer width="52%" height="100%"><PieChart><Pie data={categoryData} dataKey="value" nameKey="name" innerRadius={66} outerRadius={93} paddingAngle={3} stroke="none">{categoryData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />)}</Pie><Tooltip formatter={(value) => currency.format(value)} /></PieChart></ResponsiveContainer><div className="category-list">{categoryData.slice(0, 5).map((category, index) => <div className="category-row" key={category.name}><span><i style={{ background: COLORS[index % COLORS.length] }} />{category.name}</span><strong>{currency.format(category.value)}</strong></div>)}</div></div></div></section>

            <section className="bottom-grid"><div className="panel transactions-panel"><PanelHeading title="Recent transactions" subtitle="Your latest activity" action={<button className="text-button">See all <ArrowUpRight size={14} /></button>} /><div className="transaction-list">{recentTransactions.map((transaction) => <div className="transaction-row" key={transaction.id}><div className={`transaction-icon ${transaction.type.toLowerCase()}`}>{transaction.type === 'Income' ? <ArrowDownRight size={17} /> : <ArrowUpRight size={17} />}</div><div className="transaction-main"><strong>{transaction.merchant || transaction.description}</strong><span>{transaction.category} · {transaction.date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</span></div><strong className={transaction.type === 'Income' ? 'income-text' : ''}>{transaction.type === 'Income' ? '+' : '-'}{currency.format(transaction.amount)}</strong></div>)}</div></div><div className="panel insight-panel"><div className="insight-orbit"><Sparkles size={20} /></div><p className="kicker">Your weekly insight</p><h2>You&apos;re building a healthy savings habit.</h2><p>Your savings rate is <strong>{metrics.rate.toFixed(1)}%</strong> this period. That&apos;s above the recommended 20% target.</p><button className="secondary-button">Explore insights <ArrowUpRight size={15} /></button></div></section>
          </> : <FeaturePage view={activeView} transactions={filteredTransactions} />}
          <footer className="disclaimer">FinSight is an educational financial analysis tool. It does not provide financial advice.</footer>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ label, value, delta, detail, icon: Icon, tone, negative }) { return <div className={`metric-card ${tone}`}><div className="metric-icon"><Icon size={18} /></div><span className="metric-label">{label}</span><strong className="metric-value">{currency.format(value)}</strong><span className="metric-detail"><b className={negative ? 'negative' : ''}>{negative ? '↓' : '↑'} {delta}</b> {detail}</span></div>; }
function PanelHeading({ title, subtitle, action }) { return <div className="panel-heading"><div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div>; }

function viewFromPath(pathname) {
  return Object.entries(VIEW_ROUTES).find(([, path]) => path === pathname)?.[0] || 'Overview';
}

const VIEW_ROUTES = {
  Overview: '/',
  Transactions: '/transactions',
  'Expense Analysis': '/expense-analysis',
  Budget: '/budget',
  'Monthly Summary': '/monthly-summary',
  Insights: '/insights',
  'Import Data': '/import-data',
  Settings: '/settings',
};

function pathForView(view) {
  return VIEW_ROUTES[view] || '/';
}

function FeaturePage({ view, transactions }) {
  const expenses = transactions.filter((item) => item.type === 'Expense');
  const income = transactions.filter((item) => item.type === 'Income');
  const totalExpenses = expenses.reduce((sum, item) => sum + item.amount, 0);
  const totalIncome = income.reduce((sum, item) => sum + item.amount, 0);
  const categories = [...expenses.reduce((map, item) => map.set(item.category, (map.get(item.category) || 0) + item.amount), new Map()).entries()].sort((a, b) => b[1] - a[1]);
  const descriptions = {
    Transactions: 'Review, search, and manage every transaction in one place.',
    'Expense Analysis': 'Understand the categories, merchants, and patterns shaping your spending.',
    Budget: 'Set monthly guardrails and keep your spending aligned with your priorities.',
    'Monthly Summary': 'A clean month-by-month view of income, expenses, and savings.',
    Insights: 'Deterministic insights generated from your cleaned financial data.',
    'Import Data': 'Bring in a CSV export and let the validation and cleaning pipeline do the work.',
    Settings: 'Manage your workspace preferences and data connection.',
  };
  return <div className="feature-view"><div className="feature-hero"><div><p className="kicker">FinSight workspace</p><h2>{view}</h2><p>{descriptions[view]}</p></div><button className="secondary-button"><Settings size={15} /> Configure view</button></div>{view === 'Transactions' ? <div className="panel transactions-panel"><PanelHeading title="All transactions" subtitle={`${transactions.length} records in the current period`} action={<button className="primary-button"><Plus size={15} /> Add transaction</button>} /><div className="transaction-list">{transactions.slice(0, 18).map((item) => <div className="transaction-row" key={item.id}><div className={`transaction-icon ${item.type.toLowerCase()}`}>{item.type === 'Income' ? <ArrowDownRight size={17} /> : <ArrowUpRight size={17} />}</div><div className="transaction-main"><strong>{item.merchant || item.description}</strong><span>{item.category} · {item.date.toLocaleDateString('en-IN')}</span></div><strong className={item.type === 'Income' ? 'income-text' : ''}>{item.type === 'Income' ? '+' : '-'}{currency.format(item.amount)}</strong></div>)}</div></div> : <><div className="feature-stat-grid"><div className="panel feature-stat"><span>Total income</span><strong>{currency.format(totalIncome)}</strong></div><div className="panel feature-stat"><span>Total expenses</span><strong>{currency.format(totalExpenses)}</strong></div><div className="panel feature-stat"><span>Net savings</span><strong>{currency.format(totalIncome - totalExpenses)}</strong></div></div><div className="panel"><PanelHeading title={view === 'Insights' ? 'What the data says' : 'Category breakdown'} subtitle="Based on the current API dataset" />{categories.slice(0, 8).map(([category, amount], index) => <div className="feature-bar" key={category}><div><span>{category}</span><strong>{currency.format(amount)}</strong></div><i><b style={{ width: `${Math.max(4, (amount / (categories[0]?.[1] || 1)) * 100)}%`, background: COLORS[index % COLORS.length] }} /></i></div>)}</div></>}</div>;
}

createRoot(document.getElementById('root')).render(<BrowserRouter><App /></BrowserRouter>);
