# Contributing to MAMA-LENS AI

Thank you for your interest in MAMA-LENS AI. This project exists to reduce
maternal mortality and support women across underserved African communities.
Every contribution is welcome.

---

## Getting Started

1. Fork the repository and clone your fork
2. Follow the installation instructions in [README.md](README.md)
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes, test them, and commit
5. Open a pull request against the `master` branch

---

## Project Structure

| Directory | What lives here |
|---|---|
| `backend/api/` | FastAPI backend, routes, database models |
| `apps/web/` | React + TypeScript frontend |
| `ai/risk-engine/` | Pregnancy risk ML model and training pipeline |
| `ai/mama_model/` | flan-t5 fine-tuning and local inference |
| `ai/emotion-ai/` | EPDS scoring and emotion detection |
| `ai/nlp/` | Conversational AI, intent classification |
| `docs/` | Architecture, business, and submission documentation |

---

## Development Guidelines

- Python 3.11 required for backend and AI components
- Follow existing code style — no linter config is enforced but keep it consistent
- All new API endpoints must be added to the router in `backend/api/app/api/v1/router.py`
- Risk scoring thresholds must reference a published clinical source (WHO, IADPSG, or equivalent)
- Do not commit `.env` files, model weights (`.joblib`, `.safetensors`), or virtual environments
- Keep multilingual support in mind — English and Swahili are the primary languages

---

## Reporting Issues

Open a GitHub issue with:
- A clear description of the bug or feature request
- Steps to reproduce (for bugs)
- Expected vs actual behaviour

---

## Clinical Content

Any changes to clinical thresholds, risk scoring logic, or health advice must
cite a peer-reviewed source or WHO guideline. MAMA-LENS AI serves real women
in high-stakes healthcare contexts — accuracy matters.

---

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE).

---

*Built with compassion for African mothers.*
