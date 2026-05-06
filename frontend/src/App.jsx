import React, { useState, useEffect, useRef } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Activity, RefreshCw, Database,
  Cpu, CheckCircle2, AlertCircle, BarChart3, Settings, ShieldCheck,
  MessageSquare, Send, X, Bot, Zap
} from 'lucide-react';

const API_BASE = 'http://localhost:7772/api';

export default function App() {
  const [data, setData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [modelInfo, setModelInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [error, setError] = useState(null);
  
  // Chatbot State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'bot', content: 'Bună! Sunt asistentul tău financiar AI. Te pot ajuta cu informații despre cursul BNR, prognoze sau pot actualiza datele pentru tine. Ce dorești să afli?' }
  ]);
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dataRes = await fetch(`${API_BASE}/rates`);
      if (!dataRes.ok) throw new Error('Nu s-au găsit date. Asigurați-vă că serverul rulează pe portul 7772.');
      const dataJson = await dataRes.json();
      
      const parsedData = dataJson.data.map(item => {
        const plnKey = Object.keys(item).find(key => key !== 'Data');
        return {
          Data: item.Data,
          PLN: parseFloat(item[plnKey]).toFixed(4)
        };
      });
      
      setData(parsedData);
      
      try {
        const modelRes = await fetch(`${API_BASE}/runs?limit=1`);
        if (modelRes.ok) {
          const modelJson = await modelRes.json();
          setModelInfo(modelJson[0] || null);
          
          try {
            const predRes = await fetch(`${API_BASE}/forecast/latest`);
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

  const runPipeline = async (isAuto = false) => {
    if (!isAuto) {
      if (data.length > 0) {
        const latestDateStr = data[data.length - 1].Data;
        const latestDate = new Date(latestDateStr);
        const today = new Date();
        const diffTime = Math.abs(today - latestDate);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays <= 2) {
          const force = confirm(`Sistem Sincronizat: Datele sunt deja la zi (ultima actualizare: ${latestDateStr}).\n\nDoriți totuși să forțați o re-antrenare a modelului?`);
          if (!force) return;
        } else {
          if (!confirm("Confirmare: Acest proces va descărca cele mai noi date valutare și va reantrena modelul AI. Durează 1-2 minute.")) return;
        }
      }
    }

    try {
      setPipelineRunning(true);
      const res = await fetch(`${API_BASE}/scrape`, { method: 'POST' });
      if (!res.ok) throw new Error('A apărut o eroare de comunicare cu nucleul de procesare.');
      await fetchData();
      return true;
    } catch (err) {
      console.error(err);
      return false;
    } finally {
      setPipelineRunning(false);
    }
  };

  // AGENTIC LOGIC: SIMULATED LLM WITH TOOL CALLING
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = chatInput;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput('');

    // Simulate Agent processing
    setTimeout(async () => {
      const inputLower = userMsg.toLowerCase();
      
      // TOOL DETECTION
      if (inputLower.includes('actualizează') || inputLower.includes('scrape') || inputLower.includes('date noi')) {
        setMessages(prev => [...prev, { 
          role: 'system', 
          content: 'TOOL CALL: {"function": "scrape_bnr_data", "params": {}}' 
        }]);
        
        const success = await runPipeline(true);
        if (success) {
          setMessages(prev => [...prev, { role: 'bot', content: 'Am actualizat datele cu succes de la BNR și am reantrenat modelul AI. Dashboard-ul a fost reîmprospătat!' }]);
        } else {
          setMessages(prev => [...prev, { role: 'bot', content: 'A apărut o problemă la actualizarea datelor. Te rog să încerci din nou manual.' }]);
        }
      } 
      else if (inputLower.includes('prognoză') || inputLower.includes('predicție') || inputLower.includes('viitor')) {
        setMessages(prev => [...prev, { 
          role: 'system', 
          content: 'TOOL CALL: {"function": "get_forecast", "params": {"target": "PLN"}}' 
        }]);
        
        if (predictions.length > 0) {
          const nextVal = predictions[0].Predictie;
          setMessages(prev => [...prev, { role: 'bot', content: `Conform modelului meu XGBoost, valoarea prognozată pentru următoarea zi lucrătoare este ${nextVal} RON. Poți vedea detaliile complete în panoul de predicții.` }]);
        } else {
          setMessages(prev => [...prev, { role: 'bot', content: 'Momentan nu am o prognoză activă. Ar trebui să actualizăm datele mai întâi.' }]);
        }
      }
      else if (inputLower.includes('curs') || inputLower.includes('istoric') || inputLower.includes('cât este')) {
        setMessages(prev => [...prev, { 
          role: 'system', 
          content: 'TOOL CALL: {"function": "get_rates", "params": {"currency": "PLN"}}' 
        }]);
        
        if (data.length > 0) {
          const last = data[data.length - 1];
          setMessages(prev => [...prev, { role: 'bot', content: `Ultimul curs raportat de BNR pentru PLN este ${last.PLN} RON (la data de ${last.Data}).` }]);
        }
      }
      else {
        setMessages(prev => [...prev, { role: 'bot', content: 'Nu sunt sigur cum să te ajut cu asta. Poți să mă întrebi despre cursul actual, prognoza pe 7 zile sau să-mi ceri să actualizez datele.' }]);
      }
    }, 600);
  };

  const latestRate = data.length > 0 ? parseFloat(data[data.length - 1].PLN) : 0;
  const prevRate = data.length > 1 ? parseFloat(data[data.length - 2].PLN) : 0;
  const isUp = latestRate > prevRate;
  
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
      
      {/* PROFESSIONAL LOADING OVERLAY */}
      {pipelineRunning && (
        <div className="loading-overlay">
          <div className="loading-icon-wrapper">
            <Cpu size={40} color="#10b981" />
          </div>
          <div style={{ textAlign: 'center' }}>
            <h2 className="loading-title">Procesare Agentică în Curs</h2>
            <p className="loading-subtitle">
              Sistemul execută Tool-ul de Scraping și reantrenează modelul XGBoost...
            </p>
          </div>
          <div className="loading-steps">
            <div className="loading-step active"><RefreshCw size={16} className="spin" /> Sincronizare BNR...</div>
            <div className="loading-step active"><Activity size={16} className="spin" /> Optimizare AI...</div>
          </div>
        </div>
      )}

      <header>
        <div>
          <div className="header-title">
            <ShieldCheck size={32} color="#10b981" />
            <h1>Dashboard BNR Agentic</h1>
          </div>
          <p className="subtitle">Sistem AI cu Tool-Calling pentru analiză valutară PLN/RON</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-secondary" onClick={fetchData} disabled={pipelineRunning}>
            <RefreshCw size={16} /> Refresh Data
          </button>
          <button 
            className="btn btn-primary" 
            onClick={() => runPipeline()} 
            disabled={pipelineRunning}
          >
            <Cpu size={16} /> Actualizează & Reantrenează
          </button>
        </div>
      </header>

      {error ? (
        <div className="glass-panel" style={{ borderColor: 'var(--danger)', background: 'rgba(239, 68, 68, 0.05)' }}>
          <div className="metric-title" style={{ color: 'var(--danger)' }}>
            <AlertCircle size={20} /> Eroare Conexiune API (Port 7772)
          </div>
          <p style={{ marginTop: '1rem', color: '#f8fafc' }}>{error}</p>
        </div>
      ) : (
        <div className="dashboard-grid">
          <div className="glass-panel metric-card">
            <div className="metric-title"><Activity size={16} /> Curs Actual</div>
            <div className="metric-value">{latestRate.toFixed(4)} <span style={{fontSize:'1rem', color:'var(--text-muted)'}}>RON</span></div>
            <span className={`metric-trend ${isUp ? 'trend-up' : 'trend-down'}`}>
              {isUp ? <TrendingUp size={14} /> : <TrendingDown size={14} />} {Math.abs(latestRate - prevRate).toFixed(4)} diferență
            </span>
          </div>

          <div className="glass-panel metric-card">
            <div className="metric-title"><Cpu size={16} /> Status Model</div>
            <div className="metric-value" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '1.75rem' }}>
              {modelInfo ? <><CheckCircle2 size={28} color="var(--success)" /> Operațional</> : <><AlertCircle size={28} color="var(--warning)" /> Inactiv</>}
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
              {modelInfo ? `Ultima antrenare: ${modelInfo.trained_at}` : 'Necesită inițializare.'}
            </div>
          </div>

          <div className="glass-panel metric-card">
            <div className="metric-title"><Database size={16} /> Date Istorice</div>
            <div className="metric-value">{data.length} <span style={{fontSize:'1rem', color:'var(--text-muted)'}}>Zile</span></div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
              Ultima dată: {data.length > 0 ? data[data.length-1].Data : 'N/A'}
            </div>
          </div>

          <div className="glass-panel chart-container">
            <div className="metric-title" style={{ marginBottom: '1.5rem' }}>
              <BarChart3 size={16} /> Analiză Evoluție și Proiecție AI (7 Zile)
            </div>
            <ResponsiveContainer width="100%" height="88%">
              <AreaChart data={chartData}>
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
                <XAxis dataKey="Data" stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} minTickGap={40} />
                <YAxis domain={['auto', 'auto']} stroke="#64748b" tick={{fill: '#64748b', fontSize: 11}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px' }}
                  itemStyle={{ color: '#f8fafc' }}
                />
                <Area type="monotone" dataKey="PLN" stroke="#94a3b8" fill="url(#colorPln)" />
                <Area type="monotone" dataKey="Predictie" stroke="#10b981" strokeDasharray="5 5" fill="url(#colorPred)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {predictions.length > 0 && (
            <div className="glass-panel" style={{ gridColumn: 'span 12', padding: '1.5rem' }}>
              <div className="metric-title"><Zap size={16} /> Predicții AI Detaliate</div>
              <div className="prediction-grid">
                {predictions.map((pred, idx) => {
                  const prevVal = idx === 0 ? latestRate : predictions[idx - 1].Predictie;
                  const diff = pred.Predictie - prevVal;
                  return (
                    <div className="prediction-card" key={pred.Data}>
                      <div className="pred-date">{pred.Data}</div>
                      <div className="pred-val">{pred.Predictie.toFixed(4)}</div>
                      <div className={`pred-trend ${diff >= 0 ? 'trend-up' : 'trend-down'}`}>
                        {diff >= 0 ? <TrendingUp size={12}/> : <TrendingDown size={12}/>} {Math.abs(diff).toFixed(4)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          <div className="glass-panel table-container">
            <div className="metric-title" style={{ marginBottom: '1.25rem' }}><Database size={16} /> Istoric Recent</div>
            <table>
              <thead><tr><th>Data</th><th>Valoare</th><th>Evoluție</th></tr></thead>
              <tbody>
                {[...data].reverse().slice(0, 5).map((row, idx, arr) => {
                  const diff = idx < arr.length - 1 ? row.PLN - arr[idx+1].PLN : 0;
                  return (
                    <tr key={row.Data}>
                      <td>{row.Data}</td>
                      <td style={{ fontWeight: 600 }}>{row.PLN}</td>
                      <td>
                        <span className={`metric-trend ${diff >= 0 ? 'trend-up' : 'trend-down'}`}>
                          {diff >= 0 ? <TrendingUp size={12}/> : <TrendingDown size={12}/>} {Math.abs(diff).toFixed(4)}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* AGENTIC CHATBOT WIDGET */}
      <div className={`chat-fab ${isChatOpen ? 'active' : ''}`} onClick={() => setIsChatOpen(!isChatOpen)}>
        {isChatOpen ? <X size={24} /> : <MessageSquare size={24} />}
      </div>

      {isChatOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <Bot size={20} color="#10b981" />
            <div style={{ fontWeight: 600 }}>Asistent Agentic BNR</div>
          </div>
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-message message-${m.role}`}>
                {m.content}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form className="chat-input-area" onSubmit={handleChatSubmit}>
            <input 
              type="text" 
              className="chat-input" 
              placeholder="Întreabă AI-ul..." 
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button type="submit" className="chat-send-btn">
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
