# Contributing to StrataSentry-NWIS

Welcome to the **StrataSentry-NWIS** development community. We welcome contributions from drilling engineers, geoscientists, software architects, and machine learning researchers.

---

## 1. Development Principles

1. **Safety & Real-Time First**: Code that touches real-time streaming or risk detection loops must avoid memory leaks, blocking I/O, and unbounded computational complexity.
2. **Physics Grounding**: Pure black-box machine learning approaches must be paired with physics-based validation models (Bingham hydraulics, ECD, torque & drag, mass balance).
3. **Comprehensive Unit Testing**: All physics calculations, geometry algorithms, and extractors must have unit test coverage verifying accuracy against known petroleum engineering reference test cases.
4. **Reproducibility**: Datasets, embeddings, and model checkpoints must be versioned.

---

## 2. Setting Up the Development Environment

```bash
# Clone the repository
git clone https://github.com/oil-india-consortium/stratasentry-nwis.git
cd stratasentry-nwis

# Setup virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Install backend dependencies
pip install -r apps/api/requirements.txt
pip install pytest flake8 black mypy

# Setup Frontend
cd apps/dashboard
npm install
cd ../..
```

---

## 3. Code Standards & Tooling

- **Python**:
  - Follow PEP 8 style guidelines.
  - Formatter: `black --line-length 100`
  - Linter: `flake8`
  - Type checking: `mypy --ignore-missing-imports`
- **TypeScript / React**:
  - ESLint with TypeScript rules enabled.
  - Functional components with strict typing.
  - Three.js components must cleanly dispose of geometries and materials on unmount.

---

## 4. Running the Test Suite

```bash
# Run all unit tests
pytest services/ tests/ apps/api/tests/ -v

# Run physics verification specifically
pytest services/physics-validation/tests/ -v

# Verify Minimum Curvature Method directional surveys
pytest services/well-geometry/tests/ -v
```

---

## 5. Submitting Changes

1. Create a descriptive feature branch: `feature/kick-detection-filter` or `fix/mcm-dogleg-edge-case`.
2. Ensure all tests pass and documentation is updated.
3. Submit a Pull Request with a clear description of the petroleum engineering basis or software improvement.
