# Strategic Roadmap V3.0

This document serves as the strategic compass for `duplifinder`. It balances innovation with stability, ensuring we build a robust platform while chasing ambitious goals.

**Legend**:
- `[Debt]`: Technical debt, refactoring, or maintenance.
- `[Feat]`: New user-facing functionality.
- `[Bug]`: Fixes for known issues.
- `[Docs]`: Documentation improvements.

---

## 🏁 Phase 0: The Core (Stability & Debt)
**Goal**: Solid foundation. Ensure the current codebase is rock-solid before adding complexity.

- [ ] **Testing**: Coverage > 95%. `[Debt]` (Size: M)
  - *Context*: Current coverage is ~91%. Need to cover edge cases in `application.py` and `cache.py`.
- [ ] **Refactoring**: Simplify `application.py` orchestration. `[Debt]` (Size: L)
  - *Context*: The orchestration logic is complex and hard to test. Needs breaking down.
- [ ] **CI/CD**: Enforce strict type checking (mypy strict mode). `[Debt]` (Size: S)
  - *Context*: Ensure no implicit optionals or untyped defs slip through.
- [ ] **Documentation**: Developer Architecture Guide. `[Docs]` (Size: M)
  - *Context*: Create `CONTRIBUTING.md` with detailed architecture diagrams for new contributors.
- [ ] **Error Handling**: Standardize Exception Hierarchy. `[Debt]` (Size: S)
  - *Context*: Ensure all modules use the `DuplifinderError` base class consistently.

---

## 🚀 Phase 1: The Standard (Feature Parity)
**Goal**: Competitiveness. Match and exceed standard industry tools.
*Risk*: Low.

- [ ] **UX**: Interactive Terminal UI (TUI). `[Feat]` (Size: L)
  - *Context*: Allow users to explore duplicates interactively.
  - *Dependencies*: Requires stable core API.
- [ ] **UX**: Git "Blame" Integration. `[Feat]` (Size: M)
  - *Context*: Show who introduced the duplicate code.
- [ ] **Config**: Environment Variable Support. `[Feat]` (Size: S)
  - *Context*: Allow overriding config via `DUPLIFINDER_CONFIG_VAR`.
- [ ] **Performance**: Full Async Pipeline. `[Feat]` (Size: XL)
  - *Context*: Move file I/O and processing to a fully async event loop.
  - *Dependencies*: Requires Refactoring from Phase 0.

---

## 🔌 Phase 2: The Ecosystem (Integration)
**Goal**: Interoperability. Make `duplifinder` a platform, not just a tool.
*Risk*: Medium (Requires API design freeze).

- [ ] **API**: Public Python API. `[Feat]` (Size: L)
  - *Context*: Allow other Python tools to import and use `duplifinder` as a library.
  - *Dependencies*: Requires Phase 1 Refactoring.
- [ ] **API**: REST API / Server Mode. `[Feat]` (Size: XL)
  - *Context*: Run as a server to accept code snippets and return duplicates.
- [ ] **Plugins**: Extension System. `[Feat]` (Size: XL)
  - *Context*: Allow third-party finders and reporters.
- [ ] **Integration**: GitHub Action (Official). `[Feat]` (Size: S)
  - *Context*: Marketplace action for zero-config CI.

---

## 🔮 Phase 3: The Vision (Innovation)
**Goal**: Market Leader. Industry-disrupting capabilities.
*Risk*: High (R&D).

- [ ] **AI**: LLM-Powered Refactoring. `[Feat]` (Size: XXL)
  - *Context*: Automatically rewrite duplicates into shared abstractions.
  - *Dependencies*: Requires API from Phase 2.
- [ ] **Cloud**: Kubernetes/Docker Native. `[Feat]` (Size: L)
  - *Context*: Distributed scanning for massive monorepos.
- [ ] **Analysis**: Semantic Code Search. `[Feat]` (Size: XL)
  - *Context*: Vector embeddings to find logic that *does* the same thing but *looks* different.
