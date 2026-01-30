import Head from "next/head";
import { useState, useEffect, useCallback, useRef } from "react";

interface TokenizeResult {
  tokens: string[];
  ids: number[];
  count: number;
  error?: {
    code:
    | "MODEL_NOT_READY"
    | "TOKENIZE_FAILED"
    | "BAD_REQUEST"
    | "METHOD_NOT_ALLOWED";
  };
}

// Color palette for token visualization - enhanced dark mode colors
const TOKEN_COLORS = [
  "bg-yellow-200 dark:bg-yellow-500/20 dark:border dark:border-yellow-500/30",
  "bg-purple-200 dark:bg-purple-500/20 dark:border dark:border-purple-500/30",
  "bg-green-200 dark:bg-green-500/20 dark:border dark:border-green-500/30",
  "bg-orange-200 dark:bg-orange-500/20 dark:border dark:border-orange-500/30",
  "bg-blue-200 dark:bg-blue-500/20 dark:border dark:border-blue-500/30",
  "bg-pink-200 dark:bg-pink-500/20 dark:border dark:border-pink-500/30",
  "bg-indigo-200 dark:bg-indigo-500/20 dark:border dark:border-indigo-500/30",
  "bg-red-200 dark:bg-red-500/20 dark:border dark:border-red-500/30",
  "bg-teal-200 dark:bg-teal-500/20 dark:border dark:border-teal-500/30",
  "bg-cyan-200 dark:bg-cyan-500/20 dark:border dark:border-cyan-500/30",
];

function friendlyErrorMessage(code: NonNullable<TokenizeResult["error"]>["code"]) {
  switch (code) {
    case "MODEL_NOT_READY":
      return "Tokenizer is warming up. Please try again in a few seconds.";
    case "BAD_REQUEST":
      return "Please enter some text to tokenize.";
    case "METHOD_NOT_ALLOWED":
      return "Unsupported request.";
    case "TOKENIZE_FAILED":
    default:
      return "Something went wrong while tokenizing. Please try again.";
  }
}

export default function Home() {
  const [text, setText] = useState("नमस्कार मि एक गढ़वळि टोकनिज़र छो।");
  const [result, setResult] = useState<TokenizeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [showWhitespace, setShowWhitespace] = useState(true);
  const [uiError, setUiError] = useState<string | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      textareaRef.current?.select();
      document.execCommand("copy");
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const examples: Array<{ label: string; text: string }> = [
    { label: "Garhwali", text: "नमस्कार मि एक गढ़वळि टोकनिज़र छो।" },
    { label: "Mixed", text: "नमस्कार! This is a mixed sentence with English + देवनागरी." },
    { label: "Numbers", text: "आज तारीख 2026-01-29 छ, कीमत ₹1,23,456.78" },
    { label: "Emoji", text: "hello 👋🏽 how are you? 🤖✨" },
    { label: "Whitespace", text: "hello   world\t\tnew\nline" },
    {
      label: "Code", text: `संख्याएं = [1, 2, 3, 4, 5]
व्यक्ति = {"नाम": "राम", "शहर": "देहरादून"}

print(संख्याएं)
print(व्यक्ति["नाम"])` },
  ];

  const applyExample = async (value: string) => {
    setText(value);
    setUiError(null);
    textareaRef.current?.focus();
    // Tokenize immediately without waiting for state update
    setLoading(true);
    try {
      const response = await fetch("/api/tokenize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: value }),
      });
      const data: TokenizeResult = await response.json();
      setResult(data);
      if (!response.ok || data.error) {
        setUiError(
          friendlyErrorMessage((data.error?.code ?? "TOKENIZE_FAILED") as NonNullable<
            TokenizeResult["error"]
          >["code"])
        );
      }
    } catch {
      setResult({ tokens: [], ids: [], count: 0, error: { code: "TOKENIZE_FAILED" } });
      setUiError("Something went wrong while tokenizing. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleTokenize = useCallback(async () => {
    if (!text.trim()) {
      setUiError("Please enter some text to tokenize.");
      return;
    }

    setLoading(true);
    setUiError(null);
    try {
      const response = await fetch("/api/tokenize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data: TokenizeResult = await response.json();
      setResult(data);
      if (!response.ok || data.error) {
        setUiError(
          friendlyErrorMessage((data.error?.code ?? "TOKENIZE_FAILED") as NonNullable<
            TokenizeResult["error"]
          >["code"])
        );
      }
    } catch {
      setResult({
        tokens: [],
        ids: [],
        count: 0,
        error: { code: "TOKENIZE_FAILED" },
      });
      setUiError("Something went wrong while tokenizing. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [text]);

  // Auto-tokenize on mount with default text
  useEffect(() => {
    handleTokenize();
  }, [handleTokenize]);

  // Focus textarea on page load/refresh
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const renderToken = (token: string, index: number) => {
    const colorClass = TOKEN_COLORS[index % TOKEN_COLORS.length];
    // Replace any spaces within the token with interpunct
    const displayToken = showWhitespace
      ? token.replace(/ /g, "·")
      : token;

    const isHovered = hoveredIndex === index;

    return (
      <span
        key={index}
        onMouseEnter={() => setHoveredIndex(index)}
        onMouseLeave={() => setHoveredIndex(null)}
        className={[
          colorClass,
          "px-1 py-0.5 rounded text-sm font-mono text-gray-900 dark:text-slate-100 dark:backdrop-blur-sm",
          "transition-shadow cursor-default",
          isHovered
            ? "ring-2 ring-blue-500/70 dark:ring-blue-300/80 shadow-sm dark:bg-blue-300/10"
            : "ring-0",
        ].join(" ")}
      >
        {displayToken}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950 flex flex-col transition-colors">
      <Head>
        <title>GBM Tokenizer</title>
        <meta name="description" content="GBM SentencePiece tokenizer playground." />
      </Head>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 max-w-7xl flex-1">
        {/* Header */}
        <header className="mb-6 sm:mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-slate-50">
            (iso-639-3: gbm){" "}
            <a
              href="https://en.wikipedia.org/wiki/Garhwali_language"
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
            >
              Garhwali
            </a>{" "}
            Tokenizer
          </h1>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {/* Left Column - Input */}
          <div className="space-y-4">
            <button
              onClick={handleTokenize}
              disabled={loading || !text.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 disabled:bg-gray-400 dark:disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-all text-base sm:text-lg shadow-sm dark:shadow-blue-500/20"
            >
              {loading ? "Tokenizing..." : "Tokenize"}
            </button>

            {/* Examples */}
            <div className="border border-gray-200 dark:border-slate-800 rounded-lg p-3 bg-white/60 dark:bg-slate-950/40">
              <div className="text-xs font-semibold text-gray-600 dark:text-slate-400 mb-2">
                Examples
              </div>
              <div className="flex flex-wrap gap-2">
                {examples.map((ex) => (
                  <button
                    key={ex.label}
                    type="button"
                    onClick={() => applyExample(ex.text)}
                    className="px-2 py-1 text-xs rounded-md border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 text-gray-700 dark:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-900 transition-colors"
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="relative border border-gray-300 dark:border-slate-800 rounded-lg overflow-hidden shadow-sm dark:shadow-lg dark:shadow-black/20">
              <textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter text to tokenize..."
                className="w-full h-64 sm:h-96 p-4 pr-12 text-sm sm:text-base font-mono resize-none focus:outline-none focus:ring-0 bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 placeholder-gray-500 dark:placeholder-gray-500"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                    handleTokenize();
                  }
                }}
              />
              <button
                type="button"
                onClick={handleCopy}
                className="absolute bottom-2 right-2 p-1.5 rounded-md bg-white/90 dark:bg-slate-800/90 border border-gray-200 dark:border-slate-700 text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200 hover:bg-white dark:hover:bg-slate-800 transition-colors"
                title="Copy text"
              >
                {copied ? (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="text-green-600 dark:text-green-400"
                  >
                    <path d="M20 6L9 17l-5-5" />
                  </svg>
                ) : (
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Right Column - Output */}
          <div className="space-y-4 min-w-0">
            {/* Friendly error banner (never shows raw backend error text) */}
            {uiError && (
              <div className="border border-red-200 dark:border-red-500/30 rounded-lg p-3 sm:p-4 bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-200">
                <div className="text-sm font-medium">Couldn’t tokenize</div>
                <div className="text-sm mt-1 wrap-break-word">{uiError}</div>
              </div>
            )}
            {/* Token Count */}
            {result && (
              <div className="border border-gray-300 dark:border-slate-800 rounded-lg p-4 bg-gray-50 dark:bg-slate-900/50 shadow-sm dark:shadow-lg dark:shadow-black/20 min-w-0">
                <div className="text-sm font-semibold text-gray-700 dark:text-slate-400 mb-2">
                  Token count
                </div>
                <div className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-slate-50">
                  {result.error ? "—" : result.count}
                </div>
              </div>
            )}

            {/* Token Visualization */}
            {result && !result.error && result.tokens.length > 0 && (
              <div className="border border-gray-300 dark:border-slate-800 rounded-lg p-4 bg-gray-50 dark:bg-slate-900/50 shadow-sm dark:shadow-lg dark:shadow-black/20">
                <div className="text-sm font-semibold text-gray-700 dark:text-slate-400 mb-3">
                  Tokens
                </div>
                <div className="flex flex-wrap gap-1 items-center min-h-[80px] sm:min-h-[100px]">
                  {result.tokens.map((token, index) => (
                    <span key={index}>
                      {renderToken(token, index)}
                      {index < result.tokens.length - 1 && showWhitespace && (
                        <span className="text-gray-400 dark:text-slate-600 mx-0.5">·</span>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Token IDs */}
            {result && !result.error && result.ids.length > 0 && (
              <div className="border border-gray-300 dark:border-slate-800 rounded-lg p-4 bg-gray-50 dark:bg-slate-900/50 shadow-sm dark:shadow-lg dark:shadow-black/20">
                <div className="text-sm font-semibold text-gray-700 dark:text-slate-400 mb-3">
                  Token IDs
                </div>
                <div className="font-mono text-xs sm:text-sm text-gray-800 dark:text-slate-300 overflow-x-auto max-h-48 min-w-0">
                  <div className="flex flex-wrap gap-x-1 gap-y-1">
                    {result.ids.map((id, index) => {
                      const isHovered = hoveredIndex === index;
                      return (
                        <span key={index} className="inline-flex items-center">
                          <span
                            onMouseEnter={() => setHoveredIndex(index)}
                            onMouseLeave={() => setHoveredIndex(null)}
                            className={[
                              "px-1 py-0.5 rounded",
                              "transition-colors cursor-default",
                              isHovered
                                ? "bg-blue-100 text-blue-900 dark:bg-blue-400/20 dark:text-blue-50 ring-1 ring-blue-500/40 dark:ring-blue-300/50 border border-blue-500/30 dark:border-blue-300/40"
                                : "bg-transparent",
                            ].join(" ")}
                          >
                            {id}
                          </span>
                          {index < result.ids.length - 1 && (
                            <span className="text-gray-400 dark:text-slate-600">,</span>
                          )}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Show Whitespace Toggle */}
            {result && !result.error && (
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="showWhitespace"
                  checked={showWhitespace}
                  onChange={(e) => setShowWhitespace(e.target.checked)}
                  className="w-4 h-4 text-blue-600 dark:text-blue-500 border-gray-300 dark:border-slate-700 rounded focus:ring-blue-500 dark:focus:ring-blue-400 dark:bg-slate-800 dark:checked:bg-blue-500"
                />
                <label
                  htmlFor="showWhitespace"
                  className="text-sm text-gray-700 dark:text-slate-300 cursor-pointer"
                >
                  Show whitespace
                </label>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-slate-800/50 mt-auto transition-colors bg-white dark:bg-slate-950">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 max-w-7xl">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            {/* Left side - Attribution */}
            <div className="text-sm text-gray-600 dark:text-slate-500 text-center sm:text-left">
              Built by{" "}
              <a
                href="https://sumitesh.xyz"
                target="_blank"
                rel="noreferrer"
                className="text-gray-800 dark:text-slate-300 hover:text-gray-900 dark:hover:text-slate-200 underline transition-colors"
              >
                Sumitesh Naithani
              </a>
              . UI styling inspired by{" "}
              <a
                href="https://github.com/dqbd/tiktokenizer"
                target="_blank"
                rel="noreferrer"
                className="text-gray-800 dark:text-slate-300 hover:text-gray-900 dark:hover:text-slate-200 underline transition-colors"
              >
                tiktokenizer
              </a>
              .
            </div>

            {/* Right side - Social icons */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/sumitesh9/gbm-tokenizer"
                target="_blank"
                rel="noreferrer"
                className="text-gray-600 dark:text-slate-500 hover:text-gray-900 dark:hover:text-slate-300 transition-colors"
                aria-label="GitHub"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="lucide lucide-github"
                >
                  <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
                  <path d="M9 18c-4.51 2-5-2-7-2"></path>
                </svg>
              </a>
              <a
                href="https://in.linkedin.com/in/sumitesh9"
                target="_blank"
                rel="noreferrer"
                className="text-gray-600 dark:text-slate-500 hover:text-gray-900 dark:hover:text-slate-300 transition-colors"
                aria-label="LinkedIn"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path>
                  <rect x="2" y="9" width="4" height="12"></rect>
                  <circle cx="4" cy="4" r="2"></circle>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
