# Contributing to Mail AI

Thank you for your interest in contributing to **Mail AI**! We welcome contributions to make cold email automation safer, more deliverable, and easier for everyone.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/tanmay0401/mail-ai.git
   cd mail-ai
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Guidelines

- **Code Quality**: Keep functions modular and well-documented.
- **Privacy & Safety First**: NEVER commit `.env`, credentials, real contact lists, or personal documents.
- **Run Tests**: Verify tests pass before opening a Pull Request:
  ```bash
  python -m unittest discover -s tests
  ```

## Submitting Pull Requests

1. Create a feature branch: `git checkout -b feat/your-feature-name`
2. Commit your changes with clear, concise messages.
3. Push to your branch: `git push origin feat/your-feature-name`
4. Open a Pull Request against the `main` branch.
