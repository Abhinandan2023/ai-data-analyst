import { useEffect, useMemo, useState } from 'react'
import './index.css'

const API = '/api'

function formatColumnName(column) {
  return String(column).replace(/_/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function formatCellValue(value) {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'object') return JSON.stringify(value)
  if (typeof value === 'string' && /^-?\d+(\.\d+)?$/.test(value.trim())) {
    const number = Number(value)
    if (Number.isFinite(number)) {
      return Number.isInteger(number)
        ? number.toLocaleString('en-IN')
        : number.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
    }
  }
  if (typeof value === 'number') {
    return Number.isInteger(value)
      ? value.toLocaleString('en-IN')
      : value.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
  }
  return String(value)
}

function ResultsTable({ rows }) {
  if (!Array.isArray(rows) || rows.length === 0) return null
  const columns = Object.keys(rows[0] || {})
  if (!columns.length) return null
  return (
    <section className="results-table-card">
      <div className="results-table-header">
        <div>
          <h3>Query results</h3>
          <p className="table-subtitle">Your data, returned by the query</p>
        </div>
        <span className="results-table-count">{rows.length} {rows.length === 1 ? 'record' : 'records'}</span>
      </div>
      <div className="results-table-scroll">
        <table className="results-table">
          <thead><tr>{columns.map((column) => <th key={column} scope="col">{formatColumnName(column)}</th>)}</tr></thead>
          <tbody>
            {rows.map((row, rowIndex) => (
              <tr key={row.id ?? rowIndex}>
                {columns.map((column) => <td key={column}>{formatCellValue(row[column])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function App() {
  const [question, setQuestion] = useState('')
  const [originalQuestion, setOriginalQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showSql, setShowSql] = useState(false)
  const [historySearch, setHistorySearch] = useState('')
  const [showHistory, setShowHistory] = useState(false)
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('analyst-history') || '[]')
    } catch {
      return []
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem('analyst-history', JSON.stringify(history))
    } catch (storageError) {
      console.error('Unable to save analysis history:', storageError)
    }
  }, [history])

  async function analyze(questionText, selectedOption = null) {
    const cleanQuestion = questionText.trim()
    if (!cleanQuestion || loading) return
    setLoading(true)
    setError('')
    setResult(null)
    setShowSql(false)
    setOriginalQuestion(cleanQuestion)
    setQuestion(cleanQuestion)
    try {
      const response = await fetch(`${API}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: cleanQuestion, selected_option: selectedOption }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Unable to analyze your question.')
      }
      const normalizedData = { ...data, rows: Array.isArray(data.rows) ? data.rows : [] }
      setResult(normalizedData)
      if (normalizedData.answer && !normalizedData.clarification_question) {
        setHistory((previous) => [
          {
            question: cleanQuestion,
            answer: normalizedData.answer,
            sql: normalizedData.sql,
            rows: normalizedData.rows,
            date: new Date().toISOString(),
          },
          ...previous.filter((item) => item.question !== cleanQuestion),
        ].slice(0, 10))
      }
    } catch (err) {
      setError(err.message === 'Failed to fetch'
        ? 'Cannot connect to the backend. Check that FastAPI is running.'
        : err.message)
    } finally {
      setLoading(false)
    }
  }

  function startNewAnalysis() {
    setQuestion('')
    setOriginalQuestion('')
    setResult(null)
    setError('')
    setShowSql(false)
    setShowHistory(false)
  }

  function openHistoryItem(item) {
    setQuestion(item.question)
    setOriginalQuestion(item.question)
    setResult({
      status: 'completed',
      answer: item.answer,
      sql: item.sql,
      rows: Array.isArray(item.rows) ? item.rows : [],
      clarification_question: null,
      clarification_options: [],
    })
    setError('')
    setShowSql(false)
    setShowHistory(false)
  }

  const suggestions = [
    { icon: '♙', title: 'Top customers', question: 'Which customer has spent the most?', detail: 'Find your highest-spending customer' },
    { icon: '▥', title: 'Revenue trends', question: 'Show total revenue by month', detail: 'See how revenue changes over time' },
    { icon: '◇', title: 'Product performance', question: 'Which product sells the most?', detail: 'Discover your best-selling products' },
    { icon: '▤', title: 'Order analysis', question: 'How many orders are there?', detail: 'Understand your order volume' },
    { icon: '◷', title: 'Average order value', question: 'What is the average order value?', detail: 'Measure average spend per order' },
    { icon: '♧', title: 'Customer overview', question: 'Show all customers', detail: 'Explore your customer records' },
  ]

  const filteredHistory = useMemo(() => {
    const search = historySearch.trim().toLowerCase()
    if (!search) return history
    return history.filter((item) => item.question.toLowerCase().includes(search))
  }, [history, historySearch])

  const needsClarification = Boolean(result?.clarification_question && result?.clarification_options?.length)
  const hasRows = Array.isArray(result?.rows) && result.rows.length > 0

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={startNewAnalysis} type="button" aria-label="InsightAI home">
          <span className="brand-icon" aria-hidden="true">▥</span>
          <span className="brand-copy"><strong>Insight<span>AI</span></strong><small>AI DATA ANALYST</small></span>
        </button>

        <button className="new-analysis" onClick={startNewAnalysis} type="button">
          <span aria-hidden="true">＋</span> New analysis
        </button>

        <div className="sidebar-heading">WORKSPACE</div>
        <div className="sidebar-nav-item active"><span aria-hidden="true">⌂</span> New analysis</div>
        <button className={`sidebar-nav-item nav-button ${showHistory ? "active" : ""}`} onClick={() => setShowHistory(true)} type="button"><span aria-hidden="true">◷</span> History</button>
        <div className="sidebar-heading recent-heading">RECENT QUESTIONS</div>
        <div className="history-list">
          {filteredHistory.length === 0 ? (
            <p className="empty-history">{history.length ? 'No questions match your search.' : 'Your recent analyses will appear here.'}</p>
          ) : filteredHistory.map((item, index) => (
            <button className="history-item" key={`${item.date}-${index}`} onClick={() => openHistoryItem(item)} type="button" title={item.question}>
              <span className="history-symbol" aria-hidden="true">▢</span>
              <span className="history-question">{item.question}</span>
            </button>
          ))}
        </div>

        <div className="sidebar-promo">
          <span className="promo-icon" aria-hidden="true">✳</span>
          <h3>Good questions.<br />Clear answers.</h3>
          <p>Explore your business data with simple, natural language.</p>
        </div>

        <div className="sidebar-footer"><span className="status-dot" /><span>Workspace ready</span></div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-separator">/</span><strong>Data analysis</strong></div>
          <div className="topbar-actions">
            <label className="history-search">
              <span aria-hidden="true">⌕</span>
              <input value={historySearch} onChange={(event) => setHistorySearch(event.target.value)} placeholder="Search recent questions" aria-label="Search recent questions" />
            </label>
            <span className="connection-pill"><span className="status-dot" /> Connected</span>
          </div>
        </header>

        <section className="workspace">
          <section className="welcome">
            <div className="welcome-copy">
              <div className="eyebrow">AI DATA ANALYST</div>
              <h1>Ask your data <span>anything.</span></h1>
              <p>Get useful insights from your database using everyday language. No SQL expertise required.</p>
            </div>
            <div className="welcome-art" aria-hidden="true">
              <div className="art-orbit orbit-one" />
              <div className="art-orbit orbit-two" />
              <div className="art-chart"><i /><i /><i /><i /></div>
              <div className="art-query">Find insights<br />in your data <span>↗</span></div>
              <span className="art-spark spark-one">✳</span><span className="art-spark spark-two">✦</span>
            </div>
          </section>

          <form className="query-box" onSubmit={(event) => { event.preventDefault(); analyze(question) }}>
            <div className="query-input-row">
              <span className="query-spark" aria-hidden="true">✧</span>
              <div className="query-input-wrap">
                <label htmlFor="question">What would you like to know?</label>
                <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="e.g. Who are my top customers by total spending?" rows={2} maxLength={1000} disabled={loading} />
              </div>
            </div>
            <div className="query-box-footer">
              <span>Ask in plain English. InsightAI will do the analysis.</span>
              <button type="submit" className="ask-button" disabled={!question.trim() || loading}>
                {loading ? 'Analyzing…' : 'Analyze question'} <span aria-hidden="true">{loading ? '◌' : '↗'}</span>
              </button>
            </div>
          </form>

          {!result && !loading && !error && (
            <section className="suggestions-section">
              <div className="suggestions-heading"><div><span className="section-label">GET STARTED</span><h2>Try asking something</h2></div><p>Choose an example to run it</p></div>
              <div className="suggestions">
                {suggestions.map((suggestion) => (
                  <button className="suggestion" key={suggestion.title} type="button" onClick={() => { setQuestion(suggestion.question); analyze(suggestion.question) }}>
                    <span className="suggestion-icon" aria-hidden="true">{suggestion.icon}</span>
                    <span className="suggestion-copy"><strong>{suggestion.title}</strong><small>{suggestion.detail}</small></span>
                    <span className="suggestion-arrow" aria-hidden="true">↗</span>
                  </button>
                ))}
              </div>
            </section>
          )}

          {loading && (
            <div className="feedback-card">
              <div className="loader" />
              <div><strong>Working on your question</strong><p>Understanding your request, checking the data, and preparing your result…</p></div>
            </div>
          )}

          {error && (
            <div className="error-card" role="alert">
              <div className="error-symbol" aria-hidden="true">!</div>
              <div className="error-content"><strong>We couldn't complete that analysis</strong><p>{error}</p><button className="secondary-button" type="button" onClick={() => analyze(originalQuestion || question)}>Try again</button></div>
            </div>
          )}

          {result && (
            <section className="results-section">
              <div className="results-header">
                <div><div className="section-label">YOUR ANALYSIS</div><h2>{needsClarification ? 'One quick clarification' : 'Here are your insights'}</h2><p className="result-question">Question: {originalQuestion || question}</p></div>
                <span className="result-status"><span className="status-dot" />{needsClarification ? 'Needs clarification' : result.status || 'Completed'}</span>
              </div>

              {needsClarification ? (
                <div className="clarification-card">
                  <div className="card-icon" aria-hidden="true">?</div>
                  <div className="clarification-content"><h3>What do you mean by that?</h3><p>{result.clarification_question}</p>
                    <div className="option-list">{result.clarification_options.map((option) => (
                      <button className="option-button" key={option.value} disabled={loading} type="button" onClick={() => analyze(originalQuestion, option.value)}>
                        <span className="option-check" aria-hidden="true">↗</span><span className="option-label">{option.label}</span><span className="option-arrow" aria-hidden="true">→</span>
                      </button>
                    ))}</div>
                  </div>
                </div>
              ) : (
                <>
                  <div className="answer-card">
                    <div className="answer-card-top"><div className="answer-label"><span className="answer-icon" aria-hidden="true">✧</span><span>INSIGHT SUMMARY</span></div><span className="answer-badge">AI generated</span></div>
                    {!hasRows && <p className="answer-text">{result.answer || 'No answer was returned.'}</p>}
                    {hasRows && <p className="answer-text compact-answer">{result.answer || `Your query returned ${result.rows.length} ${result.rows.length === 1 ? 'record' : 'records'}.`}</p>}
                    {hasRows && <div className="result-mini-summary"><span className="mini-summary-icon" aria-hidden="true">✓</span>{result.rows.length.toLocaleString('en-IN')} {result.rows.length === 1 ? 'record returned' : 'records returned'}<span className="summary-divider" /> Results are ready to explore below.</div>}
                  </div>

                  {hasRows && <ResultsTable rows={result.rows} />}

                  {result.sql && (
                    <section className="sql-card">
                      <button className="sql-toggle" type="button" onClick={() => setShowSql((visible) => !visible)} aria-expanded={showSql}>
                        <span><span className="code-icon" aria-hidden="true">{'</>'}</span><span><strong>Generated SQL</strong><small>Inspect the query used for this result</small></span></span><span className="sql-toggle-action">{showSql ? 'Hide query −' : 'View query ＋'}</span>
                      </button>
                      {showSql && <div className="sql-content"><pre>{result.sql}</pre><button className="secondary-button" type="button" onClick={async () => { try { await navigator.clipboard.writeText(result.sql) } catch (copyError) { console.error('Unable to copy SQL:', copyError) } }}>Copy SQL</button></div>}
                    </section>
                  )}
                </>
              )}
              <button className="start-over" type="button" onClick={startNewAnalysis}><span aria-hidden="true">＋</span> Start a new analysis</button>
            </section>
          )}
        </section>

        {showHistory && (
          <div className="history-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setShowHistory(false) }}>
            <section className="history-dialog" role="dialog" aria-modal="true" aria-labelledby="history-title">
              <div className="history-dialog-header">
                <div><span className="section-label">YOUR WORKSPACE</span><h2 id="history-title">Analysis history</h2><p>Revisit questions you've analyzed before.</p></div>
                <button className="history-close" type="button" onClick={() => setShowHistory(false)} aria-label="Close history">×</button>
              </div>
              <label className="history-dialog-search"><span aria-hidden="true">⌕</span><input value={historySearch} onChange={(event) => setHistorySearch(event.target.value)} placeholder="Search your analyses" autoFocus /></label>
              {filteredHistory.length === 0 ? (
                <div className="history-empty-state"><span aria-hidden="true">◷</span><strong>{history.length ? 'No matching analyses' : 'Your history is empty'}</strong><p>{history.length ? 'Try a different search term.' : 'Run a question and your completed analyses will appear here.'}</p></div>
              ) : (
                <div className="history-dialog-list">
                  {filteredHistory.map((item, index) => (
                    <button className="history-dialog-item" key={`${item.date}-${index}`} type="button" onClick={() => openHistoryItem(item)}>
                      <span className="history-dialog-icon" aria-hidden="true">▤</span>
                      <span className="history-dialog-copy"><strong>{item.question}</strong><small>{item.date ? new Date(item.date).toLocaleString() : 'Saved analysis'}</small>{item.answer && <span className="history-dialog-answer">{item.answer}</span>}</span>
                      <span className="history-dialog-arrow" aria-hidden="true">↗</span>
                    </button>
                  ))}
                </div>
              )}
              <div className="history-dialog-footer"><span>{history.length} saved {history.length === 1 ? 'analysis' : 'analyses'}</span><button className="secondary-button" type="button" onClick={() => { setShowHistory(false); startNewAnalysis() }}>＋ New analysis</button></div>
            </section>
          </div>
        )}
        <footer className="page-footer"><span><strong>InsightAI</strong> · AI Data Analyst</span><span>Natural language <i>·</i> SQL <i>·</i> Insights</span></footer>
      </main>
    </div>
  )
}

export default App
