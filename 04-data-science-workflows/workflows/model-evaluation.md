# Model Evaluation Workflow

[Home](../../README.md) > [DS Workflows](../README.md) > [Workflows](README.md) > Model Evaluation

---

## Purpose

Comprehensive model evaluation to ensure models are properly assessed before deployment.

---

## When to Use

- After training any model
- Before deploying to production
- When comparing model versions
- During model review/audit

---

## Prerequisites

- Trained model
- Held-out test set (never seen during training)
- Baseline model or metrics for comparison
- Clear definition of success criteria

---

## Workflow Steps

### 1. Establish Baseline

**Goal:** Set a comparison point for model performance

**Actions:**
```python
# Classification baseline: majority class
baseline_pred = [y_train.mode()[0]] * len(y_test)
baseline_acc = accuracy_score(y_test, baseline_pred)
print(f"Majority class baseline accuracy: {baseline_acc:.4f}")

# Regression baseline: mean prediction
baseline_pred = [y_train.mean()] * len(y_test)
baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
print(f"Mean baseline RMSE: {baseline_rmse:.4f}")
```

**Checkpoint:**
- [ ] Baseline established
- [ ] Baseline performance documented

**Document:**
- Baseline type (majority class, mean, simple model)
- Baseline metrics

---

### 2. Primary Metrics

**Goal:** Calculate core performance metrics

**For Classification:**
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report
)

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # For binary

print("Classification Report:")
print(classification_report(y_test, y_pred))

metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred, average='weighted'),
    'recall': recall_score(y_test, y_pred, average='weighted'),
    'f1': f1_score(y_test, y_pred, average='weighted'),
    'roc_auc': roc_auc_score(y_test, y_prob),  # Binary only
}

for name, value in metrics.items():
    print(f"{name}: {value:.4f}")
```

**For Regression:**
```python
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error,
    r2_score, mean_absolute_percentage_error
)

y_pred = model.predict(X_test)

metrics = {
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
    'mae': mean_absolute_error(y_test, y_pred),
    'r2': r2_score(y_test, y_pred),
    'mape': mean_absolute_percentage_error(y_test, y_pred) * 100,
}

for name, value in metrics.items():
    print(f"{name}: {value:.4f}")
```

**Checkpoint:**
- [ ] Primary metrics calculated
- [ ] Metrics exceed baseline
- [ ] Metrics meet business requirements

---

### 3. Confusion Matrix (Classification)

**Goal:** Understand prediction patterns

**Actions:**
```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(8, 8))
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(ax=ax, cmap='Blues')
plt.title('Confusion Matrix')
plt.show()

# Per-class metrics
print("\nPer-class breakdown:")
for i, class_name in enumerate(model.classes_):
    tp = cm[i, i]
    fp = cm[:, i].sum() - tp
    fn = cm[i, :].sum() - tp
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    print(f"  {class_name}: precision={precision:.3f}, recall={recall:.3f}")
```

**Checkpoint:**
- [ ] Confusion patterns understood
- [ ] Problematic classes identified

**Document:**
- Classes with poor performance
- Types of errors (false positives vs false negatives)

---

### 4. ROC and PR Curves (Binary Classification)

**Goal:** Visualize threshold-dependent performance

**Actions:**
```python
from sklearn.metrics import roc_curve, precision_recall_curve, auc

# ROC Curve
fpr, tpr, roc_thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()

# PR Curve
precision, recall, pr_thresholds = precision_recall_curve(y_test, y_prob)
pr_auc = auc(recall, precision)

plt.subplot(1, 2, 2)
plt.plot(recall, precision, label=f'PR (AUC = {pr_auc:.3f})')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve')
plt.legend()

plt.tight_layout()
plt.show()
```

**Checkpoint:**
- [ ] AUC values acceptable
- [ ] Curves show clear separation from random

---

### 5. Residual Analysis (Regression)

**Goal:** Check regression assumptions and patterns

**Actions:**
```python
residuals = y_test - y_pred

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Residuals vs Predicted
axes[0, 0].scatter(y_pred, residuals, alpha=0.5)
axes[0, 0].axhline(y=0, color='r', linestyle='--')
axes[0, 0].set_xlabel('Predicted Values')
axes[0, 0].set_ylabel('Residuals')
axes[0, 0].set_title('Residuals vs Predicted')

# Residual distribution
axes[0, 1].hist(residuals, bins=50, edgecolor='black')
axes[0, 1].set_xlabel('Residual Value')
axes[0, 1].set_title('Residual Distribution')

# Q-Q plot
from scipy import stats
stats.probplot(residuals, dist="norm", plot=axes[1, 0])
axes[1, 0].set_title('Q-Q Plot')

# Predicted vs Actual
axes[1, 1].scatter(y_test, y_pred, alpha=0.5)
axes[1, 1].plot([y_test.min(), y_test.max()],
                [y_test.min(), y_test.max()], 'r--')
axes[1, 1].set_xlabel('Actual Values')
axes[1, 1].set_ylabel('Predicted Values')
axes[1, 1].set_title('Predicted vs Actual')

plt.tight_layout()
plt.show()
```

**Checkpoint:**
- [ ] Residuals appear random (no patterns)
- [ ] Residuals approximately normal
- [ ] Homoscedasticity (constant variance)

---

### 6. Feature Importance

**Goal:** Understand what drives predictions

**Actions:**
```python
# Tree-based models
if hasattr(model, 'feature_importances_'):
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    plt.figure(figsize=(10, 8))
    plt.barh(importance['feature'][:20], importance['importance'][:20])
    plt.xlabel('Importance')
    plt.title('Top 20 Feature Importances')
    plt.gca().invert_yaxis()
    plt.show()

# Permutation importance (model-agnostic)
from sklearn.inspection import permutation_importance

perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10)
perm_df = pd.DataFrame({
    'feature': feature_names,
    'importance': perm_importance.importances_mean
}).sort_values('importance', ascending=False)
```

**Checkpoint:**
- [ ] Important features make domain sense
- [ ] No unexpected features dominating

**Document:**
- Top predictive features
- Any surprising importances

---

### 7. Error Analysis

**Goal:** Understand failure modes

**Actions:**
```python
# Classification: Sample misclassified examples
errors_idx = y_test != y_pred
error_samples = X_test[errors_idx].head(20)
error_true = y_test[errors_idx].head(20)
error_pred = y_pred[errors_idx][:20]

print("Sample misclassified examples:")
for i, (idx, true, pred) in enumerate(zip(error_samples.index, error_true, error_pred)):
    print(f"\n--- Error {i+1} ---")
    print(f"True: {true}, Predicted: {pred}")
    print(f"Features: {X_test.loc[idx].to_dict()}")

# Regression: Largest errors
errors = np.abs(y_test - y_pred)
worst_idx = errors.nlargest(10).index

print("Samples with largest errors:")
for idx in worst_idx:
    print(f"\n--- Sample {idx} ---")
    print(f"Actual: {y_test.loc[idx]:.2f}, Predicted: {y_pred[y_test.index.get_loc(idx)]:.2f}")
    print(f"Error: {errors.loc[idx]:.2f}")
```

**Checkpoint:**
- [ ] Error patterns identified
- [ ] Root causes hypothesized

**Document:**
- Common failure patterns
- Potential improvements

---

### 8. Cross-Validation Stability

**Goal:** Verify performance stability

**Actions:**
```python
from sklearn.model_selection import cross_val_score

cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')

print(f"CV Scores: {cv_scores}")
print(f"Mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Check for high variance
if cv_scores.std() > 0.05:
    print("WARNING: High variance across folds - model may be unstable")
```

**Checkpoint:**
- [ ] Low variance across folds
- [ ] CV performance similar to test performance

---

### 9. Documentation

**Goal:** Create complete evaluation record

**Template:**
```markdown
## Model Evaluation Report

### Model Information
- Model type: [e.g., XGBoost Classifier]
- Training date: [date]
- Training data version: [version]
- Random seed: [seed]

### Performance Summary

| Metric | Baseline | Model | Improvement |
|--------|----------|-------|-------------|
| Accuracy | X.XX | X.XX | +X.XX |
| F1 Score | X.XX | X.XX | +X.XX |
| AUC-ROC | X.XX | X.XX | +X.XX |

### Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

### Top Features
1. feature_a (importance: X.XX)
2. feature_b (importance: X.XX)
3. feature_c (importance: X.XX)

### Error Analysis
- Most common error type: [description]
- Hypothesis for errors: [hypothesis]

### Recommendations
1. [Recommendation 1]
2. [Recommendation 2]

### Limitations
1. [Limitation 1]
2. [Limitation 2]

### Next Steps
1. [Next step 1]
2. [Next step 2]
```

---

## See Also

- **Parent**: [Workflows](README.md)
- **Previous**: [EDA Workflow](eda-workflow.md)
- **Rules**: [ML Evaluation Rules](../../08-marketplace/catalog/rules-by-domain.md)
