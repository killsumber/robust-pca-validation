#!/usr/bin/env bash

set -e

PROJECT_NAME="robust-pca-validation"

echo "Creating project: ${PROJECT_NAME}"

mkdir -p "${PROJECT_NAME}"
cd "${PROJECT_NAME}"

# =========================
# Source tree
# =========================

mkdir -p \
    src/robust_pca_validation/adapters \
    src/robust_pca_validation/datasets \
    src/robust_pca_validation/contamination \
    src/robust_pca_validation/metrics \
    src/robust_pca_validation/reference

# =========================
# Test tree
# =========================

mkdir -p \
    tests/unit

# =========================
# Python package files
# =========================

touch \
    src/robust_pca_validation/__init__.py \
    src/robust_pca_validation/adapters/__init__.py \
    src/robust_pca_validation/datasets/__init__.py \
    src/robust_pca_validation/contamination/__init__.py \
    src/robust_pca_validation/metrics/__init__.py \
    src/robust_pca_validation/reference/__init__.py \
    tests/__init__.py \
    tests/unit/__init__.py

# =========================
# Project files
# =========================

touch \
    README.md \
    pyproject.toml \
    .gitignore \
    LICENSE

# =========================
# Initial package description
# =========================

cat > src/robust_pca_validation/__init__.py <<'EOF'
"""Robust PCA validation framework."""
EOF

# =========================
# Gitignore
# =========================

cat > .gitignore <<'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.so

# Packaging
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/
env/
ENV/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Type checking
.mypy_cache/
.pyright/

# Jupyter
.ipynb_checkpoints/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Experiment outputs
results/
EOF

echo
echo "Project structure created successfully."
echo

# Show resulting tree if 'tree' is installed
if command -v tree >/dev/null 2>&1; then
    tree -a -I '.git'
else
    find . -not -path './.git*' | sort
fi