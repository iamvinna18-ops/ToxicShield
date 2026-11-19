import { useMemo, useState } from "react";
import {
  ShieldCheck, ShieldAlert, Camera, Upload, FileSpreadsheet, Languages,
  Search, Activity, MessageSquare, LayoutDashboard, Settings, Menu, X,
  ArrowRight, CheckCircle2,
} from "lucide-react";
import "./App.css";

// Change this URL only if your Flask backend uses a different address or port.
const API_URL = "http://127.0.0.1:5000/api/toxicity-check";

function App() {
  const [mode, setMode] = useState("Manual");
  const [reelUrl, setReelUrl] = useState("");
  const [comments, setComments] = useState("");
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");
  const [mobileMenu, setMobileMenu] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  const stats = useMemo(() => {
    const total = analysisResults.length;
    const spamCount = analysisResults.filter((item) => item.spam === true).length;
    const toxicCount = analysisResults.filter((item) => {
      const category = String(item.category || "").toLowerCase();
      return (category.includes("toxic") || category.includes("hate") ||
        category.includes("vulgar") || category.includes("abusive")) &&
        !category.includes("non-toxic");
    }).length;
    const safeCount = analysisResults.filter((item) => {
      const category = String(item.category || "").toLowerCase();
      return (category.includes("non-toxic") || category.includes("non toxic") ||
        category.includes("safe")) && item.spam !== true;
    }).length;
    return { total, spamCount, toxicCount, safeCount };
  }, [analysisResults]);
  const getPercentage = (count) => {
  return stats.total > 0
    ? Math.round((count / stats.total) * 100)
    : 0;
};

  function handleFile(event) {
    const selected = event.target.files?.[0];
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith(".csv")) {
      setMessage("Please select a CSV file.");
      setFile(null);
      return;
    }
    setFile(selected);
    setMessage("CSV selected. CSV analysis is not connected yet; please use Manual Input for the current test.");
  }

  async function analyzeOneComment(comment) {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comment }),
    });

    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error("The backend returned an invalid response. Check that Flask is running.");
    }
    if (!response.ok) throw new Error(data?.error || "Analysis failed.");
    return { ...data, comment: data?.comment ?? comment };
  }

  async function handleAnalyze() {
    setMessage("");
    setAnalysisError("");
    setAnalysisResults([]);

    if (mode === "Camera") {
      setMessage("Instagram Reel analysis is not connected yet. Please use Manual Input for the current detection test.");
      return;
    }
    if (mode === "csv") {
      setMessage(file
        ? "CSV upload is selected, but CSV analysis is not connected yet. Please use Manual Input for the current detection test."
        : "Please upload a CSV file.");
      return;
    }

    const commentList = comments.split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
    if (commentList.length === 0) {
      setMessage("Please enter at least one comment.");
      return;
    }

    setIsAnalyzing(true);
    try {
      // Flask currently accepts one comment per request, so send each line separately.
      const results = [];
      for (const comment of commentList) results.push(await analyzeOneComment(comment));
      setAnalysisResults(results);
      setMessage(`Analysis completed successfully for ${results.length} comment${results.length === 1 ? "" : "s"}.`);
    } catch (error) {
      setAnalysisError(error?.message || "Could not connect to the backend. Make sure your Flask server is running.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  function getResultLabel(result) {
    if (result.spam === true) return "Spam";
    const category = String(result.category || "").toLowerCase();
    if (category.includes("non-toxic") || category.includes("non toxic") || category.includes("safe")) return "Non-toxic";
    if (category.includes("toxic") || category.includes("hate") || category.includes("vulgar") || category.includes("abusive")) return "Toxic";
    return result.category || "Classified";
  }

  function getResultClass(result) {
    const label = getResultLabel(result).toLowerCase();
    if (label === "spam" || label === "toxic") return "result-bad";
    if (label === "non-toxic") return "result-good";
    return "result-neutral";
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileMenu ? "show" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><ShieldCheck size={27} /></div>
          <div><h2>ToxicShield</h2><span>AI COMMENT SECURITY</span></div>
          <button className="close-menu" onClick={() => setMobileMenu(false)} aria-label="Close menu"><X /></button>
        </div>
        <div className="nav-heading">WORKSPACE</div>
        <nav>
          <a className="nav-link active" href="#dashboard"><LayoutDashboard size={19} /> Dashboard</a>
          <a className="nav-link" href="#analyzer"><Search size={19} /> Comment Analyzer</a>
          <a className="nav-link" href="#results"><MessageSquare size={19} /> Analysis Results</a>
          <a className="nav-link" href="#analytics"><Activity size={19} /> Analytics</a>
        </nav>
        <div className="sidebar-bottom">
          <div className="security-card"><ShieldCheck size={24} /><h4>Your safety matters</h4><p>AI-powered multilingual comment moderation.</p></div>
          <a className="nav-link" href="#settings"><Settings size={19} /> Settings</a>
          <div className="version">TOXICSHIELD v1.0</div>
        </div>
      </aside>

      <main className="main-content" id="dashboard">
        <header className="topbar">
          <button className="menu-button" onClick={() => setMobileMenu(!mobileMenu)} aria-label="Toggle menu"><Menu /></button>
          <div className="breadcrumb">Workspace / <b>Dashboard</b></div>
          <div className="status"><span className="status-dot"></span> AI SYSTEM READY</div>
        </header>

        <section className="welcome-section">
          <div>
            <span className="eyebrow">INTELLIGENT CONTENT MODERATION</span>
            <h1>Protect your social space.</h1>
            <p>Detect vulgarity, hate speech, abusive language and spam comments across multiple languages.</p>
          </div>
          <div className="welcome-icon"><ShieldCheck size={76} /></div>
        </section>

        <section className="stats-grid">
          <div className="stat-card"><div className="stat-icon purple"><MessageSquare /></div><span>Total Comments</span><h2>{stats.total}</h2><small>{stats.total ? "Comments analyzed" : "Awaiting first analysis"}</small></div>
          <div className="stat-card"><div className="stat-icon red"><ShieldAlert /></div><span>Toxic Comments</span><h2>{stats.toxicCount}</h2><small>Hateful or abusive categories</small></div>
          <div className="stat-card"><div className="stat-icon orange"><Activity /></div><span>Spam Comments</span><h2>{stats.spamCount}</h2><small>Flagged as spam by the backend</small></div>
          <div className="stat-card"><div className="stat-icon green"><ShieldCheck /></div><span>Safe Comments</span><h2>{stats.safeCount}</h2><small>Classified as non-toxic or safe</small></div>
        </section>


<section className="analytics-dashboard" id="live-analytics">
  <div className="section-title">
    <div>
      <span className="eyebrow">LIVE PERFORMANCE</span>
      <h2>Detection Analytics</h2>
      <p>Real-time overview of analyzed comments.</p>
    </div>
    <span className="ai-badge">LIVE DATA</span>
  </div>

  <div className="analytics-cards">
    <div className="analytics-card">
      <div className="analytics-card-heading">
        <span>Toxic Comments</span>
        <ShieldAlert className="red-text" />
      </div>
      <h2>{getPercentage(stats.toxicCount)}%</h2>
      <div className="progress-track">
        <div className="progress-fill toxic-fill"
          style={{ width: `${getPercentage(stats.toxicCount)}%` }}
        />
      </div>
      <small>{stats.toxicCount} detected</small>
    </div>

    <div className="analytics-card">
      <div className="analytics-card-heading">
        <span>Spam Comments</span>
        <Activity className="orange-text" />
      </div>
      <h2>{getPercentage(stats.spamCount)}%</h2>
      <div className="progress-track">
        <div className="progress-fill spam-fill"
          style={{ width: `${getPercentage(stats.spamCount)}%` }}
        />
      </div>
      <small>{stats.spamCount} detected</small>
    </div>

    <div className="analytics-card">
      <div className="analytics-card-heading">
        <span>Safe Comments</span>
        <ShieldCheck className="green-text" />
      </div>
      <h2>{getPercentage(stats.safeCount)}%</h2>
      <div className="progress-track">
        <div className="progress-fill safe-fill"
          style={{ width: `${getPercentage(stats.safeCount)}%` }}
        />
      </div>
      <small>{stats.safeCount} detected</small>
    </div>
  </div>
</section>


        <section className="analyzer-section" id="analyzer">
          <div className="section-title">
            <div><span className="eyebrow">ANALYSIS CENTER</span><h2>Analyze your comments</h2><p>Choose how you want to provide your comments.</p></div>
            <span className="ai-badge"><Languages size={15} /> Multilingual AI</span>
          </div>
          <div className="mode-tabs">
            <button className={mode === "Camera" ? "selected" : ""} onClick={() => { setMode("Camera"); setMessage(""); setAnalysisError(""); }}><Camera size={18} /> Instagram Reel</button>
            <button className={mode === "csv" ? "selected" : ""} onClick={() => { setMode("csv"); setMessage(""); setAnalysisError(""); }}><FileSpreadsheet size={18} /> CSV Upload</button>
            <button className={mode === "Manual" ? "selected" : ""} onClick={() => { setMode("Manual"); setMessage(""); setAnalysisError(""); }}><MessageSquare size={18} /> Manual Input</button>
          </div>

          <div className="input-panel">
            {mode === "Camera" && <div>
              <label htmlFor="reel-url">Instagram Reel URL</label>
              <div className="url-input"><Camera size={20} /><input id="reel-url" type="url" placeholder="https://www.instagram.com/reel/..." value={reelUrl} onChange={(event) => setReelUrl(event.target.value)} /></div>
              <p className="input-help">Instagram Reel comment retrieval is not connected yet. Use Manual Input for the current detection test.</p>
            </div>}

            {mode === "csv" && <div>
              <label htmlFor="csv-file">Upload comment dataset</label>
              <label className="upload-area"><Upload size={34} /><strong>{file ? file.name : "Drop your CSV file here"}</strong><span>or click to browse your computer</span><small>CSV files only</small><input id="csv-file" type="file" accept=".csv,text/csv" onChange={handleFile} /></label>
              <p className="input-help">CSV analysis is not connected yet. Please use Manual Input for the current detection test.</p>
            </div>}

            {mode === "Manual" && <div>
              <label htmlFor="manual-comments">Paste comments</label>
              <textarea id="manual-comments" rows="6" placeholder="Paste comments here, one comment per line..." value={comments} onChange={(event) => setComments(event.target.value)} />
              <p className="input-help">Enter one comment per line. Each line will be sent to the Flask backend separately.</p>
            </div>}

            {message && <div className="message">{message}</div>}
            {analysisError && <div className="message error-message">{analysisError}</div>}
            <div className="analysis-footer">
              <div className="language-info"><Languages size={17} /> Multilingual detection<span>English, Hindi, Kannada, Telugu and more</span></div>
              <button className="analyze-button" onClick={handleAnalyze} disabled={isAnalyzing}>{isAnalyzing ? "Analyzing..." : "Analyze Comments"}<ArrowRight size={18} /></button>
            </div>
          </div>
        </section>

        <section className="bottom-grid">
          <div className="info-panel" id="results">
            <div className="panel-heading"><h3>Detection Categories</h3><span>AI CLASSIFICATION</span></div>
            <div className="category"><ShieldAlert className="red-text" /><div><b>Hate Speech</b><small>Identity-based attacks and hateful language</small></div></div>
            <div className="category"><MessageSquare className="red-text" /><div><b>Vulgarity &amp; Insults</b><small>Offensive and abusive expressions</small></div></div>
            <div className="category"><Activity className="orange-text" /><div><b>Spam &amp; Promotions</b><small>Repeated comments and suspicious links</small></div></div>
            <div className="category"><CheckCircle2 className="green-text" /><div><b>Safe Comments</b><small>Normal and non-offensive comments</small></div></div>
          </div>
          <div className="info-panel" id="analytics">
            <div className="panel-heading"><h3>Supported Languages</h3><span>LANGUAGE COVERAGE</span></div>
            <div className="language-list">{["English", "Hindi", "Kannada", "Telugu", "Tamil", "Malayalam", "Hinglish", "Other languages"].map((language) => <span key={language}>{language}</span>)}</div>
            <p className="language-note">Coverage and prediction accuracy will be evaluated separately for each language.</p>
          </div>
        </section>

        {analysisResults.length > 0 && <section className="info-panel results-panel">
          <div className="panel-heading"><h3>Latest Analysis Results</h3><span>{analysisResults.length} RESULT(S)</span></div>
          {analysisResults.map((result, index) => <div className="analysis-result" key={`${index}-${result.comment}`}>
            <div className="analysis-result-main"><p className="result-comment">{result.comment}</p><span className={`result-label ${getResultClass(result)}`}>{getResultLabel(result)}</span></div>
<div className="result-details">
  {result.confidence !== undefined && (
    <div className="result-detail-item">
      <small>AI Confidence</small>
      <strong>{Number(result.confidence).toFixed(2)}%</strong>
    </div>
  )}

  {result.spam !== undefined && (
    <div className="result-detail-item">
      <small>Spam Status</small>
      <strong>{result.spam ? "Yes" : "No"}</strong>
    </div>
  )}

  {result.spam_risk_score !== undefined && (
    <div className="result-detail-item">
      <small>Spam Risk Score</small>
      <strong>{result.spam_risk_score}</strong>
    </div>
  )}

  {result.category && (
    <div className="result-detail-item">
      <small>Detection Category</small>
      <strong>{result.category}</strong>
    </div>
  )}
</div>
     </div>)}
        </section>}

        <footer><span>© 2026 ToxicShield</span><span>AI-Powered Multilingual Comment Moderation</span></footer>
      </main>
    </div>
  );
}

export default App;