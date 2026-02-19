# Git Workflow & Contribution Guide

## 🚀 Getting Started

Clone the repository with submodules:
```bash
git clone --recursive https://github.com/welshDog/HyperCode-V2.0.git
cd HyperCode-V2.0
```

If you already cloned without recursive:
```bash
git submodule update --init --recursive
```

## 📦 Submodule Management (THE HYPERCODE)

This project uses `THE HYPERCODE` as a submodule in `THE HYPERCODE/`.

### Making Changes to Core
1. Navigate to the submodule:
   ```bash
   cd "THE HYPERCODE"
   ```
2. Make your changes, test them.
3. Commit and push **inside the submodule first**:
   ```bash
   git add .
   git commit -m "feat: my change"
   git push origin main
   ```
4. Return to root and update the pointer:
   ```bash
   cd ..
   git add "THE HYPERCODE"
   git commit -m "chore: update core submodule"
   git push origin main
   ```

### Updating Core
To pull the latest changes from the submodule remote:
```bash
git submodule update --remote
```

## 🤝 Contribution Workflow

1. **Pull Latest Changes**:
   ```bash
   git pull origin main
   git submodule update --init --recursive
   ```

2. **Create Feature Branch**:
   ```bash
   git checkout -b feat/my-feature
   ```

3. **Commit & Push**:
   ```bash
   git add .
   git commit -m "feat: description"
   git push origin feat/my-feature
   ```

4. **Merge Conflicts**:
   If you encounter conflicts, especially with submodules:
   - Resolve file conflicts as usual.
   - For submodules, ensure you are pointing to the correct commit hash.
   - Use `git status` to see what is happening.

## 🛡️ Security

- **NEVER** commit `.env` files.
- **NEVER** commit secrets or API keys.
- Use `.env.example` for templates.
- The `.gitignore` is configured to exclude sensitive files.

## 🆘 Troubleshooting

**Submodule detached HEAD?**
This is normal. If you need to commit, checkout main first:
```bash
cd "THE HYPERCODE"
git checkout main
```

**"Permission denied" on submodule push?**
You might not have write access to the submodule repo. Contact the maintainer or fork the submodule and update `.gitmodules`.
