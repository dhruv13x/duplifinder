# Duplifinder: Project Roadmap

This document outlines the strategic vision for `duplifinder`, organized by ambitious phases from core foundations to industry-disrupting capabilities. It reflects our commitment to evolving from a duplicate detection tool into an intelligent code quality ecosystem.

---

## Phase 1: Foundation (CRITICALLY MUST HAVE)

**Focus**: Core functionality, stability, security, and basic usage. These items ensure the tool is reliable, performant, and usable in standard workflows.

- [x] **AST-Powered Detection**: Core engine for finding duplicate classes, functions, and async defs.
- [x] **Text Pattern Matching**: Regex-based search for arbitrary text snippets (TODOs, FIXMEs).
- [x] **Token Similarity Analysis**: Detect near-duplicates using tokenization and similarity ratios.
- [x] **Parallel Processing**: Multithreading and multiprocessing support for high-performance scanning.
- [x] **Rich Console Output**: Human-readable, colored reports using `rich`.
- [x] **JSON Output**: Machine-readable output for CI/CD integration and external processing.
- [x] **Configuration File**: Robust configuration via `.duplifinder.yaml`.
- [x] **Enhanced Error Handling**: Granular error reporting and graceful failure modes.
- [x] **CI/CD Integration**: Exit codes, thresholds, and pipeline-friendly outputs.
- [x] **Improved Performance Metrics**: Detailed timing, memory usage, and phase breakdown stats.
- [x] **Code Coverage**: Test suite coverage exceeding 90%.
- [x] **Audit Logging**: Secure, structured logging for file access and tool operations.
- [x] **Caching**: Implement file hash caching to drastically speed up re-scans of unchanged files.
- [x] **HTML Reports**: Generate self-contained, interactive HTML reports for easier sharing and analysis.

---

## Phase 2: The Standard (MUST HAVE)

**Focus**: Feature parity with top competitors, user experience improvements, and robust developer tooling.

- [x] **Pre-commit Hook**: Official hook to prevent duplicates from entering the codebase.
- [x] **Automated Refactoring Suggestions**: Simple, actionable advice for resolving common duplication patterns.
- [x] **Support for More Languages**: Extend token/text detection to JavaScript, TypeScript, and Java.
- [ ] **Watch Mode**: "Live" scanning that updates results as you save files (DevEx improvement).
- [ ] **Git "Blame" Integration**: Identify who introduced a duplicate and when (Code ownership context).
- [ ] **Interactive Terminal UI (TUI)**: Explore duplicates directly in the terminal with keybindings.

---

## Phase 3: The Ecosystem (INTEGRATION & SHOULD HAVE)

**Focus**: Webhooks, API exposure, 3rd party plugins, SDK generation, and extensibility. Making `duplifinder` a platform.

- [ ] **GitHub Action**: Official Marketplace action for zero-config CI setup.
- [ ] **Webhook Support**: Notifications for Slack, Discord, or Microsoft Teams on new regression.
- [ ] **Plugin Architecture**: API for community-contributed finders (e.g., custom AST logic).
- [ ] **Public API / SDK**: A Python library allowing other tools to import and drive `duplifinder` programmatically.
- [ ] **Code Quality Platform Integration**: Native report formats for SonarQube, CodeClimate, and others.
- [ ] **IDE Integration**: VS Code and PyCharm extensions for inline duplicate highlighting.

---

## Phase 4: The Vision (GOD LEVEL)

**Focus**: "Futuristic" features, AI integration, advanced automation, and industry-disrupting capabilities.

- [ ] **AI-Powered Refactoring**: LLM integration to rewrite duplicated logic into shared abstractions automatically.
- [ ] **Cross-Repository Analysis**: Scan an entire GitHub organization to find duplication *between* microservices.
- [ ] **Semantic Code Search**: Vector-based embeddings to find code that *does* the same thing but *looks* different.
- [ ] **"Self-Healing" Codebase**: Autonomous agents that detect, refactor, run tests, and open PRs for duplicates.
- [ ] **Technical Debt Calculator**: Estimate the financial cost of duplication (Time × Avg Salary) to justify refactoring.
- [ ] **Predictive Analysis**: Machine learning models to identify "hotspots" likely to accumulate duplication.

---

## The Sandbox (OUT OF THE BOX / OPTIONAL)

**Focus**: Wild, creative, experimental ideas that set the project apart.

- [ ] **Gamification**: Leaderboards for "Most Unique Code" and "Top Refactorer".
- [ ] **Code Archaeology**: Timelines showing the evolution and spread of copy-pasted blocks.
- [ ] **3D Codebase Visualization**: Render the project as a city where duplicates are connected bridges.
- [ ] **Jupyter Notebook Scanning**: Special handling for `.ipynb` files to find logic duplicated across data science experiments.
- [ ] **Dependency Graph Visualization**: Visualizing how duplicates couple modules together.
