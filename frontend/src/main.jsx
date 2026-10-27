import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { HashRouter, useLocation, useNavigate } from 'react-router-dom';
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
const localDateInput = () => { const now = new Date(); return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`; };
const localMonthKey = (date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

function Root() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [authError, setAuthError] = useState(false);

  useEffect(() => {
    api.get('/auth/me').then((response) => setUser(response.data)).catch((error) => {
      if (!error.response || error.response.status >= 500) setAuthError(true);
      else setUser(null);
    }).finally(() => setChecking(false));
  }, []);

  if (checking) return <div className="auth-shell"><div className="auth-card"><div className="brand"><span className="brand-mark">F</span><span>finsight</span></div><p>Loading your secure workspace...</p></div></div>;
  if (authError) return <div className="auth-shell"><div className="auth-card"><div className="brand"><span className="brand-mark">F</span><span>finsight</span></div><h1>Service unavailable</h1><p className="auth-copy">FinSight could not reach its API. Check the API deployment and try again.</p><button className="primary-button auth-submit" onClick={() => window.location.reload()}>Retry connection</button></div></div>;
  if (!user) return <AuthScreen onAuthenticated={setUser} />;
  return <App user={user} onLogout={() => api.post('/auth/logout').finally(() => setUser(null))} />;
}

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const submit = (event) => {
    event.preventDefault();
    setBusy(true); setError('');
    api.post(`/auth/${mode}`, form).then((response) => {
      onAuthenticated(response.data.user);
    }).catch((requestError) => setError(requestError.response?.data?.detail || 'Unable to authenticate. Please try again.')).finally(() => setBusy(false));
  };
  return <div className="auth-shell"><div className="auth-card"><div className="auth-brand"><span className="brand-mark">F</span><strong>finsight</strong></div><p className="kicker">Your money, made clear</p><h1>{mode === 'login' ? 'Welcome back.' : 'Start your journey.'}</h1><p className="auth-copy">Securely track spending, understand your habits, and build a healthier financial future.</p><form onSubmit={submit} className="auth-form">{mode === 'signup' && <input required minLength="2" placeholder="Full name" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />}<input required type="email" placeholder="Email address" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /><input required minLength="8" type="password" placeholder="Password (8+ characters)" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} />{error && <p className="form-error">{error}</p>}<button className="primary-button auth-submit" disabled={busy}>{busy ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}</button></form><p className="auth-switch">{mode === 'login' ? 'New to FinSight?' : 'Already have an account?'} <button onClick={() => { setMode(mode === 'login' ? 'signup' : 'login'); setError(''); }}> {mode === 'login' ? 'Create an account' : 'Sign in'}</button></p></div></div>;
}

function App({ user, onLogout }) {
  const [transactions, setTransactions] = useState([]);
  const [query, setQuery] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [dateRange, setDateRange] = useState('Last 6 months');
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState('');
  const [insights, setInsights] = useState([]);
  const [showTransactionForm, setShowTransactionForm] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const activeView = viewFromPath(location.pathname);

  const loadTransactions = () => {
    setLoading(true);
    api.get('/insights').then((response) => setInsights(response.data)).catch(() => setInsights([]));
    setApiError('');
    api.get('/transactions')
      .then((transactionResponse) => transactionResponse.data.map((row) => ({
        ...row,
        amount: Number(row.amount),
        date: new Date(`${row.date}T00:00:00`),
      })))
      .then(setTransactions)
      .catch(() => {
        setTransactions([]);
        setApiError('The financial API is unavailable. Check the deployment and try again.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadTransactions(); }, []);

  const addTransaction = (payload) => api.post('/transactions', payload).then(() => { setShowTransactionForm(false); loadTransactions(); }).catch((error) => { throw new Error(error.response?.data?.detail || 'Could not save transaction.'); });
  const removeTransaction = (id) => {
    if (!window.confirm('Delete this transaction?')) return;
    api.delete(`/transactions/${id}`).then(loadTransactions).catch((error) => setApiError(error.response?.data?.detail || 'Could not delete the transaction.'));
  };

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
      const key = `${item.date.getFullYear()}-${String(item.date.getMonth() + 1).padStart(2, '0')}`;
      if (!months.has(key)) months.set(key, { month: item.date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }), income: 0, expenses: 0, sort: item.date.getFullYear() * 12 + item.date.getMonth() });
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
        <div className="workspace-switcher"><span className="avatar">{user.name.slice(0, 2).toUpperCase()}</span><span><strong>{user.name}&apos;s workspace</strong><small>{user.email}</small></span><button className="logout-button" onClick={onLogout} title="Sign out">↪</button></div>
        <nav className="main-nav" aria-label="Main navigation">
          <p className="eyebrow">Workspace</p>
          {navItems.map(({ label, icon: Icon }) => <button key={label} className={`nav-item ${activeView === label ? 'active' : ''}`} onClick={() => { navigate(pathForView(label)); setMenuOpen(false); }}><Icon size={18} /><span>{label}</span>{label === 'Insights' && <span className="nav-dot" />}</button>)}
          <p className="eyebrow nav-spacer">Manage</p>
          <button className={`nav-item ${activeView === 'Settings' ? 'active' : ''}`} onClick={() => navigate('/settings')}><Settings size={18} /><span>Settings</span></button>
        </nav>
        <div className="sidebar-footer"><div className="help-card"><CircleHelp size={18} /><div><strong>Need a hand?</strong><span>Read our quick guide</span></div><ArrowUpRight size={15} /></div><span className="version">Finsight v1.0 · Educational use</span></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><button className="icon-button mobile-menu" onClick={() => setMenuOpen(!menuOpen)} aria-label="Toggle navigation">{menuOpen ? <X size={20} /> : <Menu size={20} />}</button><div className="breadcrumb"><span>Workspace</span><span>/</span><strong>{activeView}</strong></div><div className="top-actions"><div className="notification-wrap"><button className="icon-button" aria-label="Notifications" onClick={() => setNotificationsOpen(!notificationsOpen)}><Bell size={19} /><i /></button>{notificationsOpen && <div className="popover"><strong>Notifications</strong><span>No new notifications</span></div>}</div><div className="top-avatar">{user.name.slice(0, 2).toUpperCase()}</div></div></header>

        <div className="content-wrap">
          <div className="page-heading"><div><p className="kicker">{new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }).format(new Date())}</p><h1>Good morning, {user.name.split(' ')[0]}<span className="accent">.</span></h1><p className="subheading">Here&apos;s what&apos;s happening with your money.</p></div><button className="primary-button" onClick={() => setShowTransactionForm(true)}><Plus size={17} /> Add transaction</button></div>
          <div className="toolbar"><div className="search-box"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search transactions" /></div><select value={dateRange} onChange={(event) => setDateRange(event.target.value)} aria-label="Date range"><option>Last 6 months</option><option>Last 12 months</option></select><button className="icon-button" aria-label="Transaction filters" onClick={() => setFiltersOpen(!filtersOpen)}><MoreHorizontal size={19} /></button>{filtersOpen && <div className="popover filter-popover"><strong>Filters</strong><button className="text-button" onClick={() => { setQuery(''); setDateRange('Last 6 months'); setFiltersOpen(false); }}>Reset filters</button></div>}</div>

          {loading ? <div className="loading-state">Loading your financial picture...</div> : apiError ? <div className="loading-state"><p>{apiError}</p><button className="secondary-button" onClick={() => window.location.reload()}>Retry</button></div> : activeView === 'Overview' ? <>
            <section className="metric-grid" aria-label="Financial summary">
              <MetricCard label="Net savings" value={metrics.savings} detail="for selected period" icon={Wallet} tone="dark" />
              <MetricCard label="Income" value={metrics.income} detail="for selected period" icon={ArrowDownRight} tone="green" />
              <MetricCard label="Expenses" value={metrics.expenses} detail="for selected period" icon={ArrowUpRight} tone="orange" />
              <div className="metric-card savings-card"><div className="metric-icon"><TrendingUp size={18} /></div><span className="metric-label">Savings rate</span><strong className="metric-value">{metrics.rate.toFixed(1)}%</strong><div className="progress-track"><span style={{ width: `${Math.max(0, Math.min(metrics.rate, 100))}%` }} /></div><span className="metric-detail">Against a 20% target <b className={metrics.rate >= 20 ? "" : "negative"}>{metrics.rate >= 20 ? "On track" : "Below target"}</b></span></div>
            </section>

            <section className="chart-grid"><div className="panel trend-panel"><PanelHeading title="Cash flow" subtitle="Income and expenses over time" action={<select value={dateRange} onChange={(event) => setDateRange(event.target.value)}><option>Last 6 months</option><option>Last 12 months</option></select>} /><div className="chart-legend"><span><i className="legend-income" />Income</span><span><i className="legend-expenses" />Expenses</span></div><div className="chart-area"><ResponsiveContainer width="100%" height="100%"><AreaChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}><defs><linearGradient id="incomeFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2f6f68" stopOpacity={0.2} /><stop offset="100%" stopColor="#2f6f68" stopOpacity={0} /></linearGradient><linearGradient id="expenseFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#d95d39" stopOpacity={0.14} /><stop offset="100%" stopColor="#d95d39" stopOpacity={0} /></linearGradient></defs><CartesianGrid vertical={false} stroke="#e9e9e3" /><XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: '#8b918b', fontSize: 12 }} /><YAxis axisLine={false} tickLine={false} tick={{ fill: '#8b918b', fontSize: 11 }} tickFormatter={(value) => `₹${compactCurrency.format(value)}`} /><Tooltip formatter={(value) => currency.format(value)} contentStyle={{ border: '1px solid #e5e6df', borderRadius: 8, boxShadow: '0 8px 20px #26352a14' }} /><Area type="monotone" dataKey="income" stroke="#2f6f68" strokeWidth={2.5} fill="url(#incomeFill)" /><Area type="monotone" dataKey="expenses" stroke="#d95d39" strokeWidth={2.5} fill="url(#expenseFill)" /></AreaChart></ResponsiveContainer></div></div><div className="panel category-panel"><PanelHeading title="Where your money goes" subtitle="Spending by category" action={<button className="text-button" onClick={() => navigate('/expense-analysis')}>View details <ArrowUpRight size={14} /></button>} /><div className="donut-wrap"><ResponsiveContainer width="52%" height="100%"><PieChart><Pie data={categoryData} dataKey="value" nameKey="name" innerRadius={66} outerRadius={93} paddingAngle={3} stroke="none">{categoryData.map((entry, index) => <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />)}</Pie><Tooltip formatter={(value) => currency.format(value)} /></PieChart></ResponsiveContainer><div className="category-list">{categoryData.slice(0, 5).map((category, index) => <div className="category-row" key={category.name}><span><i style={{ background: COLORS[index % COLORS.length] }} />{category.name}</span><strong>{currency.format(category.value)}</strong></div>)}</div></div></div></section>

            <section className="bottom-grid"><div className="panel transactions-panel"><PanelHeading title="Recent transactions" subtitle="Your latest activity" action={<button className="text-button" onClick={() => navigate('/transactions')}>See all <ArrowUpRight size={14} /></button>} /><div className="transaction-list">{recentTransactions.map((transaction) => <div className="transaction-row" key={transaction.id}><div className={`transaction-icon ${transaction.type.toLowerCase()}`}>{transaction.type === 'Income' ? <ArrowDownRight size={17} /> : <ArrowUpRight size={17} />}</div><div className="transaction-main"><strong>{transaction.merchant || transaction.description}</strong><span>{transaction.category} · {transaction.date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</span></div><strong className={transaction.type === 'Income' ? 'income-text' : ''}>{transaction.type === 'Income' ? '+' : '-'}{currency.format(transaction.amount)}</strong></div>)}</div></div><div className="panel insight-panel"><div className="insight-orbit"><Sparkles size={20} /></div><p className="kicker">Based on your transactions</p><h2>{insights[0]?.title || "Your financial insights"}</h2><p>{insights[0]?.description || "Add transactions to see patterns from your financial activity."}</p><button className="secondary-button" onClick={() => navigate('/insights')}>Explore insights <ArrowUpRight size={15} /></button></div></section>
          </> : <FeaturePage view={activeView} transactions={filteredTransactions} allTransactions={transactions} user={user} onAdd={() => setShowTransactionForm(true)} onDelete={removeTransaction} onRefresh={loadTransactions} onLogout={onLogout} />}
          <footer className="disclaimer">FinSight is an educational financial analysis tool. It does not provide financial advice.</footer>
        </div>
      </main>
      {showTransactionForm && <TransactionForm onClose={() => setShowTransactionForm(false)} onSubmit={addTransaction} />}
    </div>
  );
}

function MetricCard({ label, value, detail, icon: Icon, tone }) { return <div className={`metric-card ${tone}`}><div className="metric-icon"><Icon size={18} /></div><span className="metric-label">{label}</span><strong className="metric-value">{currency.format(value)}</strong><span className="metric-detail">{detail}</span></div>; }
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

function FeaturePage({ view, transactions, allTransactions, user, onAdd, onDelete, onRefresh, onLogout }) {
  const [insights, setInsights] = useState([]);
  const [budgets, setBudgets] = useState([]);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [budget, setBudget] = useState({ category: '', amount: '', month_year: localMonthKey(new Date()) });
  useEffect(() => {
    if (view === 'Insights') api.get('/insights').then(({ data }) => setInsights(data)).catch((e) => setError(e.response?.data?.detail || 'Could not load insights.'));
    if (view === 'Budget') api.get('/budgets').then(({ data }) => setBudgets(data)).catch((e) => setError(e.response?.data?.detail || 'Could not load budgets.'));
  }, [view]);
  const descriptions = {
    Transactions: 'Review, search, and manage every transaction in one place.',
    'Expense Analysis': 'Understand your spending by category.', Budget: 'Set monthly spending limits by category.',
    'Monthly Summary': 'Review income, expenses, and savings by month.', Insights: 'Patterns calculated from your transaction history.',
    'Import Data': 'Import a CSV export of your transactions.', Settings: 'Your workspace settings.',
  };
  const expenses = transactions.filter((item) => item.type === 'Expense');
  const income = transactions.filter((item) => item.type === 'Income');
  const totalExpenses = expenses.reduce((sum, item) => sum + item.amount, 0);
  const totalIncome = income.reduce((sum, item) => sum + item.amount, 0);
  const categories = [...expenses.reduce((map, item) => map.set(item.category, (map.get(item.category) || 0) + item.amount), new Map()).entries()].sort((a, b) => b[1] - a[1]);
  const uploadCsv = async (event) => {
    const file = event.target.files?.[0]; if (!file) return;
    setError(''); setMessage(''); const body = new FormData(); body.append('file', file);
    try { const { data } = await api.post('/import/csv', body); setMessage(`Imported ${data.imported} rows; ${data.report?.invalid_rows_removed || 0} invalid rows skipped.`); onRefresh(); }
    catch (e) { setError(e.response?.data?.detail || 'CSV import failed.'); } finally { event.target.value = ''; }
  };
  const saveBudget = async (event) => {
    event.preventDefault(); setError('');
    try { await api.post('/budgets', { ...budget, amount: Number(budget.amount) }); const { data } = await api.get('/budgets'); setBudgets(data); setBudget({ ...budget, category: '', amount: '' }); }
    catch (e) { setError(e.response?.data?.detail || 'Could not save budget.'); }
  };
  return <div className="feature-view"><div className="feature-hero"><div><p className="kicker">FinSight workspace</p><h2>{view}</h2><p>{descriptions[view]}</p></div>{view === 'Transactions' && <button className="primary-button" onClick={onAdd}><Plus size={15} /> Add transaction</button>}{view === 'Import Data' && <label className="secondary-button upload-button"><Plus size={15} /> Choose CSV<input type="file" accept=".csv,text/csv" onChange={uploadCsv} /></label>}</div>
    {error && <p className="form-error" role="alert">{error}</p>}{message && <p className="success-message" role="status">{message}</p>}
    {view === 'Transactions' && <div className="panel"><PanelHeading title="Transactions" subtitle={`${transactions.length} records in the selected period`} /><div className="transaction-list">{transactions.map((item) => <div className="transaction-row" key={item.id}><div className={`transaction-icon ${item.type.toLowerCase()}`}>{item.type === 'Income' ? <ArrowDownRight size={17} /> : <ArrowUpRight size={17} />}</div><div className="transaction-main"><strong>{item.merchant || item.description}</strong><span>{item.category} &middot; {item.date.toLocaleDateString('en-IN')}</span></div><strong className={item.type === 'Income' ? 'income-text' : ''}>{item.type === 'Income' ? '+' : '-'}{currency.format(item.amount)}</strong><button className="delete-button" onClick={() => onDelete(item.id)} aria-label={`Delete ${item.description}`}>&times;</button></div>)}</div>{!transactions.length && <p className="empty-state">No transactions match this view.</p>}</div>}
    {view === 'Import Data' && <div className="panel"><h2>Import your transaction history</h2><p>CSV must include date, description, amount, and type. Importing replaces existing transactions in this workspace.</p><a className="secondary-button" href="/data/sample_transactions.csv" download>Download sample CSV</a></div>}
    {view === 'Insights' && <div className="panel"><PanelHeading title="Insights from your data" subtitle="Calculated from your transaction history" />{insights.map((item, i) => <div className="feature-bar" key={`${item.title}-${i}`}><div><span>{item.title}</span><strong>{item.metric || ''}</strong></div><p>{item.description}</p></div>)}{!insights.length && <p className="empty-state">Add transactions to generate insights.</p>}</div>}
    {view === 'Budget' && <><form className="panel budget-form" onSubmit={saveBudget}><PanelHeading title="Monthly budgets" subtitle="Set a spending limit for each category" /><div className="form-grid"><input required placeholder="Category" value={budget.category} onChange={(e) => setBudget({ ...budget, category: e.target.value })} /><input required type="number" min="0.01" step="0.01" placeholder="Amount" value={budget.amount} onChange={(e) => setBudget({ ...budget, amount: e.target.value })} /><input required type="month" value={budget.month_year} onChange={(e) => setBudget({ ...budget, month_year: e.target.value })} /></div><button className="primary-button">Save budget</button></form><div className="panel">{budgets.map((item) => { const spent = allTransactions.filter((row) => row.type === 'Expense' && row.category.toLowerCase() === item.category.toLowerCase() && localMonthKey(row.date) === item.month_year).reduce((sum, row) => sum + row.amount, 0); return <div className="feature-bar" key={item.id}><div><span>{item.category} &middot; {item.month_year}</span><strong>{currency.format(spent)} / {currency.format(Number(item.amount))}</strong></div><i><b style={{ width: `${Math.min(100, Number(item.amount) > 0 ? spent / Number(item.amount) * 100 : 0)}%` }} /></i></div>; })}{!budgets.length && <p className="empty-state">No budgets saved yet.</p>}</div></>}
    {view === 'Settings' && <div className="panel settings-panel"><PanelHeading title="Account" subtitle="Signed-in workspace details" /><p><strong>{user.name}</strong></p><p>{user.email}</p><a className="secondary-button" href={`${import.meta.env.VITE_API_URL || '/api'}/export/csv`}>Export transactions as CSV</a><button className="text-button" onClick={onLogout}>Sign out</button></div>}
    {(view === 'Expense Analysis' || view === 'Monthly Summary') && <><div className="feature-stat-grid"><div className="panel feature-stat"><span>Total income</span><strong>{currency.format(totalIncome)}</strong></div><div className="panel feature-stat"><span>Total expenses</span><strong>{currency.format(totalExpenses)}</strong></div><div className="panel feature-stat"><span>Net savings</span><strong>{currency.format(totalIncome - totalExpenses)}</strong></div></div><div className="panel"><PanelHeading title={view === 'Monthly Summary' ? 'Monthly summary' : 'Spending by category'} subtitle="Based on your transactions" />{view === 'Monthly Summary' ? [...transactions.reduce((map, row) => { const key = localMonthKey(row.date); const v = map.get(key) || { income: 0, expenses: 0 }; v[row.type === 'Income' ? 'income' : 'expenses'] += row.amount; map.set(key, v); return map; }, new Map())].sort(([a], [b]) => b.localeCompare(a)).map(([month, v]) => <div className="feature-bar" key={month}><div><span>{month}</span><strong>Income {currency.format(v.income)} &middot; Expenses {currency.format(v.expenses)} &middot; Savings {currency.format(v.income - v.expenses)}</strong></div></div>) : categories.map(([name, amount], i) => <div className="feature-bar" key={name}><div><span>{name}</span><strong>{currency.format(amount)}</strong></div><i><b style={{ width: `${Math.max(4, amount / (categories[0]?.[1] || 1) * 100)}%`, background: COLORS[i % COLORS.length] }} /></i></div>)}</div></>}
  </div>;
}

function TransactionForm({ onClose, onSubmit }) {
  const [form, setForm] = useState({ date: localDateInput(), description: '', amount: '', type: 'Expense', category: 'Other', payment_method: 'UPI', merchant: '', notes: '' });
  const [error, setError] = useState('');
  const update = (key, value) => setForm({ ...form, [key]: value });
  return <div className="modal-backdrop"><form className="modal-card" onSubmit={(event) => { event.preventDefault(); onSubmit({ ...form, amount: Number(form.amount) }).catch((error) => setError(error.message)); }}><div className="modal-header"><div><p className="kicker">Workspace</p><h2>Add transaction</h2></div><button type="button" className="icon-button" onClick={onClose}><X size={19} /></button></div><div className="form-grid"><input required type="date" value={form.date} onChange={(event) => update('date', event.target.value)} /><select value={form.type} onChange={(event) => update('type', event.target.value)}><option>Expense</option><option>Income</option></select><input required placeholder="Description" value={form.description} onChange={(event) => update('description', event.target.value)} /><input required min="0" step="0.01" type="number" placeholder="Amount" value={form.amount} onChange={(event) => update('amount', event.target.value)} /><input placeholder="Category" value={form.category} onChange={(event) => update('category', event.target.value)} /><input placeholder="Merchant" value={form.merchant} onChange={(event) => update('merchant', event.target.value)} /></div>{error && <p className="form-error" role="alert">{error}</p>}<div className="modal-actions"><button type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button">Save transaction</button></div></form></div>;
}

createRoot(document.getElementById('root')).render(<HashRouter><Root /></HashRouter>);
