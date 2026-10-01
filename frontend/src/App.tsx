import { useState } from "react";
import type { FormEvent } from "react";

type Source = {
  page: number;
  chunk_id: string;
  score: number;
};

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
    selectedQuestion?: string
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
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: finalQuestion,
        }),
      });

      const text = await response.text();

      let data: ApiResponse;

      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          "The API returned an invalid response. Make sure FastAPI is running on port 8000."
        );
      }

      if (!response.ok) {
        throw new Error(
          data.detail ||
            data.error ||
            "Unable to process your question."
        );
      }

      setAnswer(data.answer || "No answer was returned.");
      setSources(data.sources || []);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Something went wrong.";

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
      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-icon">AI</div>

            <div>
              <h1>ABS Support AI</h1>
              <p>ABS / TBS User Manual Assistant</p>
            </div>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            RAG Assistant
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="main">
        <section className="hero">
          <div className="hero-badge">
            AI-Powered Documentation Assistant
          </div>

          <h2>
            Ask questions about the
            <span> ABS User Manual</span>
          </h2>

          <p className="hero-description">
            Get grounded answers from the ABS/TBS documentation
            using Retrieval-Augmented Generation.
          </p>
        </section>

        {/* Common questions */}
        <section className="questions-section">
          <p className="section-label">Common questions</p>

          <div className="question-list">
            {commonQuestions.map((item) => (
              <button
                key={item}
                type="button"
                className="question-chip"
                onClick={() => handleCommonQuestion(item)}
                disabled={loading}
              >
                {item}
              </button>
            ))}
          </div>
        </section>

        {/* Ask form */}
        <section className="ask-card">
          <form onSubmit={askQuestion}>
            <label htmlFor="question">Ask the manual</label>

            <div className="input-wrapper">
              <textarea
                id="question"
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="For example: How do I register as an artist?"
                rows={4}
                disabled={loading}
              />

              <button
                type="submit"
                className="ask-button"
                disabled={loading || !question.trim()}
              >
                {loading ? "Searching..." : "Ask AI"}
              </button>
            </div>
          </form>
        </section>

        {/* Error */}
        {error && (
          <section className="error-card">
            <div className="error-icon">!</div>

            <div>
              <strong>Unable to answer</strong>
              <p>{error}</p>
            </div>
          </section>
        )}

        {/* Answer */}
        {answer && !error && (
          <section className="answer-card">
            <div className="answer-header">
              <div>
                <p className="section-label">Answer</p>
                <h3>ABS Support AI</h3>
              </div>

              <div className="grounded-badge">
                Grounded in manual
              </div>
            </div>

            <div className="answer-content">
              {answer}
            </div>

            {/* Sources */}
            {sources.length > 0 && (
              <div className="sources-section">
                <p className="section-label">Sources</p>

                <div className="sources-list">
                  {sources.map((source, index) => (
                    <div
                      className="source-item"
                      key={`${source.chunk_id}-${index}`}
                    >
                      <div className="source-page">
                        Page {source.page}
                      </div>

                      <div className="source-details">
                        <strong>ABS User Manual</strong>
                        <span>{source.chunk_id}</span>
                      </div>

                      <div className="source-score">
                        {Math.round(source.score * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {/* How it works */}
        {!answer && !error && !loading && (
          <section className="how-it-works">
            <p className="section-label">How it works</p>

            <div className="steps">
              <div className="step">
                <div className="step-number">1</div>

                <div>
                  <h3>Ask</h3>
                  <p>
                    Ask a question about the ABS/TBS User Manual.
                  </p>
                </div>
              </div>

              <div className="step">
                <div className="step-number">2</div>

                <div>
                  <h3>Retrieve</h3>
                  <p>
                    The system finds the most relevant manual
                    sections.
                  </p>
                </div>
              </div>

              <div className="step">
                <div className="step-number">3</div>

                <div>
                  <h3>Answer</h3>
                  <p>
                    Gemini generates a grounded answer with
                    document sources.
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          ABS Support AI · RAG-powered documentation assistant
        </p>
      </footer>
    </div>
  );
}

export default App;