import { useState } from "react";
import type { FormEvent } from "react";
type Source = { page: number; chunk_id: string; score: number };
type ApiResponse = {
  answer?: string;
  sources?: Source[];
  error?: string;
  detail?: string;
};
const API_URL = "http://127.0.0.1:8000";
const commonQuestions = [
  "What is ABS?",
  "How do I register as an artist?",
  "How do I log in?",
  "What does a Station Admin do?",
];
function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const askQuestion = async (
    event?: FormEvent<HTMLFormElement>,
    selectedQuestion?: string,
  ) => {
    event?.preventDefault();
    const finalQuestion = (selectedQuestion ?? question).trim();
    if (!finalQuestion) {
      setError("Please enter a question.");
      return;
    }
    setQuestion(finalQuestion);
    setAnswer("");
    setSources([]);
    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: finalQuestion }),
      });
      const text = await response.text();
      let data: ApiResponse;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          "The API returned an invalid response. Make sure FastAPI is running on port 8000.",
        );
      }
      if (!response.ok) {
        throw new Error(
          data.detail || data.error || "Unable to process your question.",
        );
      }
      setAnswer(data.answer || "No answer was returned.");
      setSources(data.sources || []);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };
  const handleCommonQuestion = (selectedQuestion: string) => {
    void askQuestion(undefined, selectedQuestion);
  };
  return (
    <div className="app">
      {" "}
      {/* Government-style top strip */}{" "}
      <div className="top-strip">
        {" "}
        <div className="container top-strip-inner">
          {" "}
          <span>Government of India</span> <span>Prasar Bharati</span>{" "}
        </div>{" "}
      </div>{" "}
      {/* Header */}{" "}
      <header className="site-header">
        {" "}
        <div className="container header-inner">
          {" "}
          <div className="brand">
            {" "}
            <div className="brand-mark">
              {" "}
              <span>PB</span>{" "}
            </div>{" "}
            <div className="brand-text">
              {" "}
              <h1>Prasar Bharati</h1>{" "}
              <p>India's Public Service Broadcaster</p>{" "}
            </div>{" "}
          </div>{" "}
          <div className="product-name">
            {" "}
            <span className="product-label">AI ASSISTANT</span>{" "}
            <strong>ABS Support AI</strong>{" "}
          </div>{" "}
        </div>{" "}
      </header>{" "}
      {/* Navigation-style bar */}{" "}
      <nav className="nav-bar">
        {" "}
        <div className="container nav-inner">
          {" "}
          <span>Artist / Talent Booking System</span>{" "}
          <span className="nav-divider">|</span>{" "}
          <span>ABS / TBS User Manual</span>{" "}
        </div>{" "}
      </nav>{" "}
      <main className="container main">
        {" "}
        {/* Hero */}{" "}
        <section className="hero">
          {" "}
          <div className="hero-content">
            {" "}
            <div className="eyebrow">
              {" "}
              <span className="eyebrow-line"></span> DOCUMENTATION
              ASSISTANT{" "}
            </div>{" "}
            <h2>
              {" "}
              ABS User Manual <br /> <span>AI Support Assistant</span>{" "}
            </h2>{" "}
            <p>
              {" "}
              Ask questions about the Artist / Talent Booking System and get
              answers grounded in the official user manual.{" "}
            </p>{" "}
            <div className="hero-meta">
              {" "}
              <span>
                {" "}
                <span className="meta-dot"></span> RAG Powered{" "}
              </span>{" "}
              <span>
                {" "}
                <span className="meta-dot"></span> Manual Grounded{" "}
              </span>{" "}
              <span>
                {" "}
                <span className="meta-dot"></span> Source Referenced{" "}
              </span>{" "}
            </div>{" "}
          </div>{" "}
          <div className="hero-card">
            {" "}
            <div className="hero-card-top">
              {" "}
              <span className="ai-icon">AI</span>{" "}
              <span>ABS Support AI</span>{" "}
            </div>{" "}
            <div className="hero-card-body">
              {" "}
              <div className="mini-question">
                {" "}
                <span>You</span> <p>What is ABS?</p>{" "}
              </div>{" "}
              <div className="mini-answer">
                {" "}
                <span>AI Assistant</span>{" "}
                <p>
                  {" "}
                  ABS stands for Artist/Talent Booking Software (ABS/TBS).{" "}
                </p>{" "}
              </div>{" "}
              <div className="mini-source"> Source · Page 3 </div>{" "}
            </div>{" "}
          </div>{" "}
        </section>{" "}
        {/* Main question area */}{" "}
        <section className="assistant-section">
          {" "}
          <div className="section-heading">
            {" "}
            <div>
              {" "}
              <span className="section-kicker">ASK THE MANUAL</span>{" "}
              <h3>How can we help?</h3>{" "}
            </div>{" "}
            <span className="manual-badge"> ABS User Manual </span>{" "}
          </div>{" "}
          <div className="ask-card">
            {" "}
            <form onSubmit={askQuestion}>
              {" "}
              <label htmlFor="question"> Enter your question </label>{" "}
              <div className="input-wrapper">
                {" "}
                <textarea
                  id="question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="For example: How do I register as an artist?"
                  rows={4}
                  disabled={loading}
                />{" "}
                <div className="input-footer">
                  {" "}
                  <span className="input-hint">
                    {" "}
                    Answers are generated from the ABS/TBS User Manual.{" "}
                  </span>{" "}
                  <button
                    type="submit"
                    className="ask-button"
                    disabled={loading || !question.trim()}
                  >
                    {" "}
                    {loading ? (
                      <>
                        {" "}
                        <span className="spinner"></span> Searching...{" "}
                      </>
                    ) : (
                      <>
                        {" "}
                        Ask AI <span className="arrow">→</span>{" "}
                      </>
                    )}{" "}
                  </button>{" "}
                </div>{" "}
              </div>{" "}
            </form>{" "}
          </div>{" "}
          {/* Common questions */}{" "}
          <div className="common-section">
            {" "}
            <span className="section-kicker"> COMMON QUESTIONS </span>{" "}
            <div className="question-list">
              {" "}
              {commonQuestions.map((item) => (
                <button
                  key={item}
                  type="button"
                  className="question-chip"
                  onClick={() => handleCommonQuestion(item)}
                  disabled={loading}
                >
                  {" "}
                  <span className="chip-arrow">→</span> {item}{" "}
                </button>
              ))}{" "}
            </div>{" "}
          
          </div>{" "}
        </section>{" "}
        {/* Error */}{" "}
        {error && (
          <section className="error-card">
            {" "}
            <div className="error-icon">!</div>{" "}
            <div>
              {" "}
              <strong>Unable to answer</strong> <p>{error}</p>{" "}
            </div>{" "}
          </section>
        )}{" "}
        {/* Answer */}{" "}
        {answer && !error && (
          <section className="answer-section">
            {" "}
            <div className="answer-heading">
              {" "}
              <div>
                {" "}
                <span className="section-kicker"> AI RESPONSE </span>{" "}
                <h3>Answer from the manual</h3>{" "}
              </div>{" "}
              <span className="grounded-badge">
                {" "}
                ✓ Grounded in manual{" "}
              </span>{" "}
            </div>{" "}
            <div className="answer-card">
              {" "}
              <div className="answer-icon"> AI </div>{" "}
              <div className="answer-content"> {answer} </div>{" "}
            </div>{" "}
            {sources.length > 0 && (
              <div className="sources-section">
                {" "}
                <div className="sources-heading">
                  {" "}
                  <div>
                    {" "}
                    <span className="section-kicker">
                      {" "}
                      RETRIEVAL SOURCES{" "}
                    </span>{" "}
                    <h4>Relevant manual sections</h4>{" "}
                  </div>{" "}
                  <span className="source-count">
                    {" "}
                    {sources.length} sources{" "}
                  </span>{" "}
                </div>{" "}
                <div className="sources-list">
                  {" "}
                  {sources.map((source, index) => (
                    <div
                      className="source-item"
                      key={`${source.chunk_id}-${index}`}
                    >
                      {" "}
                      <div className="source-page">
                        {" "}
                        <span>PAGE</span> <strong>{source.page}</strong>{" "}
                      </div>{" "}
                      <div className="source-details">
                        {" "}
                        <strong>ABS User Manual</strong>{" "}
                        <span>{source.chunk_id}</span>{" "}
                      </div>{" "}
                      <div className="source-score">
                        {" "}
                        <span>Relevance</span>{" "}
                        <strong> {source.score.toFixed(2)} </strong>{" "}
                      </div>{" "}
                    </div>
                  ))}{" "}
                </div>{" "}
              </div>
            )}{" "}
          </section>
        )}{" "}
        {/* Empty state */}{" "}
        {!answer && !error && !loading && (
          <section className="how-section">
            {" "}
            <div className="section-heading">
              {" "}
              <div>
                {" "}
                <span className="section-kicker"> HOW IT WORKS </span>{" "}
                <h3>From question to answer</h3>{" "}
              </div>{" "}
            </div>{" "}
            <div className="steps">
              {" "}
              <div className="step">
                {" "}
                <div className="step-number">01</div>{" "}
                <div>
                  {" "}
                  <h4>Ask</h4>{" "}
                  <p>
                    {" "}
                    Enter a question about ABS or the TBS user manual.{" "}
                  </p>{" "}
                </div>{" "}
              </div>{" "}
              <div className="step">
                {" "}
                <div className="step-number">02</div>{" "}
                <div>
                  {" "}
                  <h4>Retrieve</h4>{" "}
                  <p>
                    {" "}
                    Relevant sections are retrieved using semantic
                    similarity.{" "}
                  </p>{" "}
                </div>{" "}
              </div>{" "}
              <div className="step">
                {" "}
                <div className="step-number">03</div>{" "}
                <div>
                  {" "}
                  <h4>Answer</h4>{" "}
                  <p>
                    {" "}
                    Gemini generates a grounded response with manual
                    references.{" "}
                  </p>{" "}
                </div>{" "}
              </div>{" "}
            </div>{" "}
          </section>
        )}{" "}
      </main>{" "}
      {/* Footer */}{" "}
      <footer className="footer">
        {" "}
        <div className="container footer-inner">
          {" "}
          <div>
            {" "}
            <strong>ABS Support AI</strong>{" "}
            <p> RAG-powered documentation assistant </p>{" "}
          </div>{" "}
          <div className="footer-right">
            {" "}
            <span>Artist / Talent Booking System</span> <span>·</span>{" "}
            <span>Prasar Bharati</span>{" "}
          </div>{" "}
        </div>{" "}
      </footer>{" "}
    </div>
  );
}
export default App;
