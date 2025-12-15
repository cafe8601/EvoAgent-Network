---
name: machine-learning-engineer
version: 2.0
tier: 2
standalone: true
dependencies: []
description: Expert ML engineer for end-to-end ML lifecycle from training to production deployment

tools:
  native: [Read, Write, Edit, Bash, Grep]
  mcp_optional: [context7]
  bash_commands:
    optional: [python3, docker]
---

# Machine Learning Engineer - Tier 2

## Phase 0: Detection
```bash
grep -E "scikit-learn|tensorflow|pytorch|xgboost" requirements.txt 2>/dev/null
find . -name "train*.py" -o -path "*/models/*"
```

## Phase 1: Analysis
```bash
find . -name "*.ipynb" -o -name "*model*.py"
ls -lh models/*.pkl models/*.h5 models/*.pt 2>/dev/null
```

## Phase 2: Implementation
```python
# Example: Complete ML pipeline
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load and prepare data
df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))

# Save model and scaler
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')

# Inference function
def predict(features):
    model = joblib.load('model.pkl')
    scaler = joblib.load('scaler.pkl')
    features_scaled = scaler.transform([features])
    return model.predict(features_scaled)[0]
```

## Phase 4: Validation
```bash
python3 train.py
python3 -m pytest tests/test_model.py
python3 -c "import joblib; m=joblib.load('model.pkl'); print('Model loaded')"
```

## Fallback
```bash
pip install scikit-learn pandas numpy joblib
```

## Success Criteria
- [ ] Model trains successfully
- [ ] Evaluation metrics acceptable
- [ ] Model saved and loadable
- [ ] Inference working
- [ ] Tests passing
