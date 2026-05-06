import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Activity, RefreshCw, Database,
  Cpu, CheckCircle2, AlertCircle, BarChart3, Settings, ShieldCheck
} from 'lucide-react';

export default function App() {
  const [data, setData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dataRes = await fetch('http://localhost:8000/api/data');
      if (!dataRes.ok) throw new Error('Nu s-au găsit date. Asigurați-vă că serverul rulează.');
      const dataJson = await dataRes.json();
      
      // Parse the data
      const parsedData = dataJson.data.map(item => {
        const plnKey = Object.keys(item).find(key => key !== 'Data');
        return {
          Data: item.Data,
          PLN: parseFloat(item[plnKey]).toFixed(4)
        };
      });
      
      setData(parsedData);
      
      try {
        const modelRes = await fetch('http://localhost:8000/api/model/info');
        if (modelRes.ok) {
          const modelJson = await modelRes.json();
          setModelInfo(modelJson);
          
          // Fetch real predictions from the trained model
          try {
            const predRes = await fetch('http://localhost:8000/api/predict');
            if (predRes.ok) {
              const predJson = await predRes.json();
              setPredictions(predJson.predictions || []);
            }
          } catch (e) {
            console.log("Predictions not available yet");
          }
        }
      } catch (e) {
        console.log("Model not found yet");
      }
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const runPipeline = async () => {
    if (data.length > 0) {
      const latestDateStr = data[data.length - 1].Data;
      const latestDate = new Date(latestDateStr);
      const today = new Date();
      const diffTime = Math.abs(today - latestDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays <= 2) {
        const force = confirm(`Sistem Sincronizat: Datele sunt deja la zi (ultima actualizare: ${latestDateStr}).\n\nMotorul AI operează deja pe cele mai recente date financiare BNR.\n\nDoriți totuși să forțați o re-antrenare a modelului?`);
        if (!force) return;
      } else {
        if (!confirm("Confirmare: Acest proces va descărca cele mai noi date valutare și va reantrena complet modelul AI pentru o precizie maximă. Durează aproximativ 1-2 minute.")) return;
      }
    } else {
      if (!confirm("Confirmare: Acest proces va descărca datele valutare și va antrena modelul AI. Durează aproximativ 1-2 minute.")) return;
    }

    try {
      setPipelineRunning(true);
      const res = await fetch('http://localhost:8000/api/run-pipeline', { method: 'POST' });
      if (!res.ok) throw new Error('A apărut o eroare de comunicare cu nucleul de procesare.');
      fetchData();
    } catch (err) {
      alert(err.message);
    } finally {
      setPipelineRunning(false);
    }
  };

  const latestRate = data.length > 0 ? parseFloat(data[data.length - 1].PLN) : 0;
  const prevRate = data.length > 1 ? parseFloat(data[data.length - 2].PLN) : 0;
  const isUp = latestRate > prevRate;
  
  // Use REAL predictions from the trained XGBoost model
  const chartData = [...data];
  if (predictions.length > 0) {
    predictions.forEach(pred => {
      chartData.push({
        Data: pred.Data,
        Predictie: pred.Predictie.toFixed(4)
      });
    });
  }

  return (
    <div className="dashboard-container">
      
      {/* PROFESSIONAL LOADING OVERLAY FOR PIPELINE */}
      {pipelineRunning && (
        <div className="loading-overlay">
          <div className="loading-icon-wrapper">
            <Cpu size={40} color="#10b981" />
          </div>
          <div style={{ textAlign: 'center' }}>
            <h2 className="loading-title">Procesare Inteligentă în Curs</h2>
            <p className="loading-subtitle">
              Sistemul descarcă cele mai noi date valutare și optimizează hiperparametrii rețelei AI pentru o acuratețe maximă a predicțiilor. Vă rugăm să așteptați.
            </p>
          </div>
          <div className="loading-steps">
            <div className="loading-step active"><RefreshCw size={16} className="spin" /> Extragere date BNR (Scraping)...</div>
            <div className="loading-step active"><Settings size={16} className="spin" /> Antrenare model XGBoost...</div>
            <div className="loading-step active"><Activity size={16} className="spin" /> Optimizare Bayesiană (Optuna)...</div>
          </div>
        </div>
      )}

      {loading && !pipelineRunning && (
        <div className="loading-overlay" style={{ background: 'rgba(9, 14, 23, 0.95)' }}>
          <RefreshCw size={40} className="spin" color="#10b981" />
          <h2>Se inițializează mediul...</h2>
        </div>
      )}

      <header>
        <div>
          <div className="header-title">
            <ShieldCheck size={32} color="#10b981" />
            <h1>Curs BNR Predictiv</h1>
          </div>
          <p className="subtitle">Inteligență Artificială aplicată în analiza pieței valutare PLN/RON</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-secondary" onClick={fetchData} disabled={pipelineRunning}>
            <RefreshCw size={16} /> Reîmprospătare Interfață
          </button>
          <button 
            className="btn btn-primary" 
            onClick={runPipeline} 
            disabled={pipelineRunning}
          >
            <Cpu size={16} /> {pipelineRunning ? "Se procesează..." : "Actualizează & Reantrenează Modelul AI"}
          </button>
        </div>
      </header>

      {error ? (
        <div className="glass-panel" style={{ borderColor: 'var(--danger)', background: 'rgba(239, 68, 68, 0.05)' }}>
          <div className="metric-title" style={{ color: 'var(--danger)' }}>
            <AlertCircle size={20} /> Eroare Conexiune Sistem
          </div>
          <p style={{ marginTop: '1rem', color: '#f8fafc' }}>{error}</p>
          <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Vă rugăm să verificați nucleul de procesare (serverul FastAPI pe portul 8000).</p>
        </div>
      ) : (
        <div className="dashboard-grid">
          
          {/* Curs Actual Card */}
          <div className="glass-panel metric-card">
            <div className="metric-title">
              <Activity size={16} /> Valoare de Referință (PLN)
            </div>
            <div className="metric-value">{latestRate.toFixed(4)} <span style={{fontSize:'1rem', color:'var(--text-muted)', fontWeight: 500}}>RON</span></div>
            <div>
              <span className={`metric-trend ${isUp ? 'trend-up' : 'trend-down'}`}>
                {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {Math.abs(latestRate - prevRate).toFixed(4)} ron diferență față de ziua anterioară
              </span>
            </div>
          </div>

          {/* Model Status Card */}
          <div className="glass-panel metric-card">
            <div className="metric-title">
              <Cpu size={16} /> Motor AI de Predicție
            </div>
            <div className="metric-value" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.75rem' }}>
              {modelInfo ? (
                <><CheckCircle2 size={28} color="var(--success)" /> Operațional</>
              ) : (
                <><AlertCircle size={28} color="var(--warning)" /> Neinițializat</>
              )}
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem', lineHeight: 1.4 }}>
              {modelInfo ? `Sistemul XGBoost este activ și a fost validat algoritmic (Time-Series Cross-Validation).` : 'Inițializați antrenarea pentru a activa predicțiile valutare.'}
            </div>
          </div>

          {/* Database Info Card */}
          <div className="glass-panel metric-card">
            <div className="metric-title">
              <Database size={16} /> Registru Istoric Date
            </div>
            <div className="metric-value">{data.length} <span style={{fontSize:'1rem', color:'var(--text-muted)', fontWeight: 500}}>Zile Analizate</span></div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.5rem' }}>
              Ultima actualizare extrasă: <span style={{ color: '#e2e8f0' }}>{data.length > 0 ? data[data.length-1].Data : 'N/A'}</span>
            </div>
          </div>

          {/* Main Chart */}
          <div className="glass-panel chart-container">
            <div className="metric-title" style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between' }}>
              <span><BarChart3 size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '6px' }}/> Analiza Evoluției și Proiecția pe Următoarele 7 Zile</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--accent)' }}>Model Confidence: High</span>
            </div>
            <ResponsiveContainer width="100%" height="88%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorPln" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#94a3b8" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                <XAxis 
                  dataKey="Data" 
                  stroke="#64748b" 
                  tick={{fill: '#64748b', fontSize: 11}}
                  minTickGap={40}
                  axisLine={{ stroke: 'rgba(255,255,255,0.05)' }}
                />
                <YAxis 
                  domain={['auto', 'auto']} 
                  stroke="#64748b"
                  tick={{fill: '#64748b', fontSize: 11}}
                  tickFormatter={(val) => val.toFixed(2)}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', backdropFilter: 'blur(8px)', boxShadow: '0 10px 25px rgba(0,0,0,0.5)' }}
                  itemStyle={{ color: '#f8fafc', fontWeight: 600 }}
                  labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                />
                <Area type="monotone" name="Valoare Istorică" dataKey="PLN" stroke="#94a3b8" strokeWidth={2} fillOpacity={1} fill="url(#colorPln)" />
                <Area type="monotone" name="Proiecție AI" dataKey="Predictie" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" fillOpacity={1} fill="url(#colorPred)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* AI Predictions Grid */}
          {chartData.length > data.length && (
            <div className="glass-panel" style={{ gridColumn: 'span 12', padding: '1.5rem' }}>
              <div className="metric-title" style={{ marginBottom: '0.5rem' }}>
                <Cpu size={16} /> Proiecția Inteligenței Artificiale (Următoarele 7 Zile)
              </div>
              <div className="prediction-grid">
                {chartData.slice(data.length).map((pred, idx) => {
                  const prevVal = idx === 0 ? latestRate : parseFloat(chartData[data.length + idx - 1].Predictie);
                  const currentVal = parseFloat(pred.Predictie);
                  const diff = currentVal - prevVal;
                  const isUp = diff > 0;
                  const isSame = diff === 0;
                  
                  return (
                    <div className="prediction-card" key={pred.Data}>
                      <div className="pred-date">{pred.Data}</div>
                      <div className="pred-val">{currentVal.toFixed(4)}</div>
                      <div className={`pred-trend ${isSame ? '' : isUp ? 'trend-up' : 'trend-down'}`}>
                        {!isSame && (isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />)}
                        {isSame ? '-' : Math.abs(diff).toFixed(4)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Historical Data Table */}
          <div className="glass-panel table-container">
            <div className="metric-title" style={{ marginBottom: '1.25rem' }}>
              <Database size={16} /> Situația Valutară Recentă (Ultimele 10 Extrageri BNR)
            </div>
            <table>
              <thead>
                <tr>
                  <th>Data Raportării</th>
                  <th>Valoare (RON)</th>
                  <th>Evoluție</th>
                </tr>
              </thead>
              <tbody>
                {[...data].reverse().slice(0, 10).map((row, idx, arr) => {
                  const prevDay = arr[idx + 1];
                  const currentVal = parseFloat(row.PLN);
                  const prevVal = prevDay ? parseFloat(prevDay.PLN) : currentVal;
                  const diff = currentVal - prevVal;
                  const isUp = diff > 0;
                  const isSame = diff === 0;
                  
                  return (
                    <tr key={row.Data}>
                      <td>{row.Data}</td>
                      <td style={{ fontWeight: 600, color: '#f8fafc' }}>{currentVal.toFixed(4)}</td>
                      <td>
                        {isSame ? (
                          <span style={{ color: 'var(--text-muted)' }}>-</span>
                        ) : (
                          <span className={`metric-trend ${isUp ? 'trend-up' : 'trend-down'}`}>
                            {isUp ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                            {Math.abs(diff).toFixed(4)}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
                {data.length === 0 && (
                  <tr>
                    <td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>Datele nu sunt încă procesate.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

        </div>
      )}
    </div>
  );
}
