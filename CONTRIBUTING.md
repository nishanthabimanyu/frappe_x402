# Contributing to frappe_x402

First off, thank you for considering contributing to `frappe_x402`! It's people like you who will build the future of the agentic economy.

## 📜 Code of Conduct
This project follows the [Frappe Community Code of Conduct](https://frappeframework.com/docs/v14/user/en/introduction/code-of-conduct).

## 🛠 Development Workflow

### 1. Setup
Follow the installation instructions in the [README.md](README.md). We recommend using the `frappe_docker` development environment for a consistent setup.

### 2. Standards
We adhere to the high engineering standards set by **Frappe** and **rtCamp**:
- **DocType First:** Always prefer Frappe's metadata-driven approach over custom database tables.
- **Python:** Follow PEP8. Use `Black` or `Ruff` for formatting.
- **JavaScript:** Follow Frappe's standard JS conventions (standard spaces, no semicolons in Vue files).
- **Naming:** Use clear, descriptive names for fields and functions. (e.g., `total_earned_usdc` instead of `earnings`).

### 3. Submitting a Pull Request
1.  Fork the repository and create your branch from `main`.
2.  Ensure your code passes all tests: `bench --site [your-site] run-tests --app frappe_x402`.
3.  Write a clear, descriptive PR title and description.
4.  Link any relevant issues.

## 🧪 Testing
A contribution is not complete without verification. If you add a new feature or fix a bug, please include a test case in the `tests/` directory of the app.

## 💬 Communication
If you have questions or want to discuss a major feature, please open an **Issue** first.

---

Thank you for making the agentic economy more accessible!
