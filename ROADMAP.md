# Strategic Roadmap (V3.0)

This living document outlines the strategic direction for `duplifinder`, balancing innovation with stability. It follows a phased execution strategy to ensure a solid foundation before ecosystem expansion.

---

## 🏁 Phase 0: The Core (Stability & Debt)
**Goal**: Build a solid, reliable foundation. Prioritizing code quality and developer experience.

- [x] **Testing**: Maintain coverage > 90%. `[Debt]` `[S]`
- [x] **CI/CD**: Fix Linting (Ruff). `[Debt]` `[S]`
- [x] **CI/CD**: Fix Type Checking (Mypy). `[Debt]` `[S]`
- [ ] **Refactoring**: Improve `application.py` and `cache.py` structure. `[Debt]` `[M]`
- [x] **Documentation**: Comprehensive README. `[Docs]` `[S]`

---

## 🚀 Phase 1: The Standard (Feature Parity)
**Goal**: Achieve competitiveness with market standards through improved UX and configuration.

- [ ] **UX**: Interactive Terminal UI (TUI). `[Feat]` `[M]`
- [ ] **UX**: Git "Blame" Integration. `[Feat]` `[M]`
- [ ] **Config**: Robust settings management & Schema Validation. `[Feat]` `[S]`
- [ ] **Performance**: Optimization of AST visitor & Tokenizer. `[Feat]` `[M]`
- [ ] **Error Handling**: Context-aware error messages for config issues. `[Feat]` `[S]`

---

## 🔌 Phase 2: The Ecosystem (Integration)
**Goal**: Enable interoperability and extensibility.
*Requires Phase 1 completion.*

- [ ] **API**: Public Python API / SDK. `[Feat]` `[L]`
- [ ] **Plugins**: Extension system for custom finders. `[Feat]` `[L]`
- [ ] **Integration**: Official GitHub Action. `[Feat]` `[M]`
- [ ] **Integration**: Webhook Support (Slack/Teams). `[Feat]` `[S]`
- [ ] **IDE**: VS Code / PyCharm Extensions. `[Feat]` `[L]`

---

## 🔮 Phase 3: The Vision (Innovation)
**Goal**: Become the market leader through AI and Cloud capabilities.
*Requires Phase 2 completion.*

- [ ] **AI**: LLM Integration for Refactoring Suggestions. `[Feat]` `[L]` (Risk: High)
- [ ] **Cloud**: Cross-Repository Analysis. `[Feat]` `[L]`
- [ ] **Cloud**: "Self-Healing" Codebase (Auto-PRs). `[Feat]` `[L]`
- [ ] **Analytics**: Technical Debt Calculator & Trends. `[Feat]` `[M]`

---

## Legend
- **Tags**: `[Debt]` (Technical Debt), `[Feat]` (New Feature), `[Bug]` (Bug Fix), `[Docs]` (Documentation).
- **Estimates**: `[S]` (Small), `[M]` (Medium), `[L]` (Large).
