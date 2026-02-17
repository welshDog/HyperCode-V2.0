# 🤝 Contributing to HyperCode

Welcome to the HyperCode team! We're building a tool that helps developers stay in flow, and we want your help.

## 🧠 Our Philosophy: Neurodiversity First

We believe in:
- **Clarity over Brevity**: Explain *why*, not just *what*.
- **Explicit Instructions**: No "implied" requirements.
- **Psychological Safety**: It's okay to ask "stupid" questions. There are no stupid questions here.

## 🚀 How to Contribute

### 1. Found a Bug?
- Open an Issue on GitHub.
- Describe what happened, what you expected, and steps to reproduce.
- Screenshots or error logs are super helpful!

### 2. Want to Build a Feature?
- Check the **Roadmap** in `README.md` (or open a discussion).
- Fork the repository.
- Create a branch: `git checkout -b feature/amazing-feature`
- Commit your changes: `git commit -m "feat: add amazing feature"`
- Push to your branch: `git push origin feature/amazing-feature`
- Open a Pull Request.

## 📝 Commit Message Convention

We follow the **Conventional Commits** specification to keep our history clean and readable.

**Format**: `<type>(<scope>): <subject>`

**Types**:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

**Example**:
```bash
feat(auth): add google oauth login
fix(api): handle timeout in user service
docs(readme): update deployment steps
```

## 🛡️ Branch Protection & Workflow

- **Main Branch (`main`)**: Protected. Direct pushes are disabled. All changes must come via Pull Request.
- **CI/CD Checks**: All PRs must pass the automated CI/CD pipeline (tests, linting, build) before merging.
- **Code Review**: At least one approval is required from a maintainer.

## 🛠️ Development Setup

1. **Fork & Clone**
2. **Install Dependencies**
   - For Backend:
     ```bash
     cd THE\ HYPERCODE/hypercode-core
     pip install -r requirements.txt
     ```
   - For Frontend:
     ```bash
     cd BROski\ Business\ Agents/broski-terminal
     npm install
     ```
3. **Run Tests**
   ```bash
   npm test
   pytest
   ```

## 💜 Code of Conduct

Be kind. Be patient. We are all learning and building together.
- Respect different communication styles.
- Assume positive intent.
- Focus on the code, not the person.

Let's build something amazing together! 🚀

---
> *Built with WelshDog + BROski* 🚀🌙
