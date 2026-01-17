# EDA Workflow

[Home](../../README.md) > [DS Workflows](../README.md) > [Workflows](README.md) > EDA Workflow

---

## Purpose

Systematic exploratory data analysis to understand data quality, distributions, and relationships before modeling.

---

## When to Use

- Starting work with a new dataset
- After data updates or changes
- Before any modeling effort
- When debugging data issues

---

## Prerequisites

- Dataset loaded into pandas DataFrame
- Basic understanding of expected data structure
- Access to visualization libraries (matplotlib, seaborn, plotly)

---

## Workflow Steps

### 1. Initial Inspection

**Goal:** Understand data shape and structure

**Actions:**
```python
# Shape and memory
print(f"Shape: {df.shape}")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")

# Column types
print(df.dtypes)

# First/last rows
display(df.head())
display(df.tail())

# Column names
print(df.columns.tolist())
```

**Checkpoint:**
- [ ] Shape matches expectations
- [ ] Column names are correct
- [ ] Data types are appropriate

**Document:**
- Total rows and columns
- Any unexpected columns
- Memory considerations

---

### 2. Missing Values Analysis

**Goal:** Identify and characterize missing data

**Actions:**
```python
# Missing counts and percentages
missing = pd.DataFrame({
    'count': df.isnull().sum(),
    'percent': (df.isnull().sum() / len(df)) * 100
}).sort_values('percent', ascending=False)

print(missing[missing['count'] > 0])

# Visualize missing patterns
import missingno as msno
msno.matrix(df)
msno.heatmap(df)
```

**Checkpoint:**
- [ ] Missing pattern understood (random, systematic, MCAR/MAR/MNAR)
- [ ] Decision made on handling strategy

**Document:**
- Columns with significant missing data
- Hypotheses about why data is missing
- Handling strategy for each column

---

### 3. Numeric Distributions

**Goal:** Understand distributions of numeric columns

**Actions:**
```python
# Summary statistics
print(df.describe())

# Distributions
numeric_cols = df.select_dtypes(include=[np.number]).columns

for col in numeric_cols:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Histogram
    df[col].hist(bins=50, ax=axes[0])
    axes[0].set_title(f'{col} Distribution')

    # Box plot
    df[col].plot(kind='box', ax=axes[1])
    axes[1].set_title(f'{col} Box Plot')

    plt.tight_layout()
    plt.show()

    # Key statistics
    print(f"\n{col}:")
    print(f"  Mean: {df[col].mean():.2f}")
    print(f"  Median: {df[col].median():.2f}")
    print(f"  Std: {df[col].std():.2f}")
    print(f"  Skew: {df[col].skew():.2f}")
```

**Checkpoint:**
- [ ] Distributions characterized (normal, skewed, bimodal, etc.)
- [ ] Outliers identified
- [ ] Transformation needs noted

**Document:**
- Distribution shapes
- Notable outliers
- Columns needing transformation

---

### 4. Categorical Analysis

**Goal:** Understand categorical variables

**Actions:**
```python
# Identify categorical columns
cat_cols = df.select_dtypes(include=['object', 'category']).columns

for col in cat_cols:
    print(f"\n{col}:")
    print(f"  Unique values: {df[col].nunique()}")
    print(f"  Value counts:\n{df[col].value_counts().head(10)}")

    # Bar plot for low cardinality
    if df[col].nunique() <= 20:
        df[col].value_counts().plot(kind='bar')
        plt.title(f'{col} Distribution')
        plt.xticks(rotation=45)
        plt.show()
```

**Checkpoint:**
- [ ] Cardinality understood for each categorical
- [ ] Rare categories identified
- [ ] Encoding strategy determined

**Document:**
- High cardinality columns
- Rare categories to handle
- Unexpected values

---

### 5. Target Variable Analysis (if supervised)

**Goal:** Understand target distribution

**Actions:**
```python
# For classification
print(f"Target distribution:\n{df[target_col].value_counts(normalize=True)}")
df[target_col].value_counts().plot(kind='bar')

# For regression
df[target_col].hist(bins=50)
print(f"Target statistics:\n{df[target_col].describe()}")
```

**Checkpoint:**
- [ ] Class balance assessed (classification)
- [ ] Distribution characterized (regression)
- [ ] Stratification needs determined

**Document:**
- Class imbalance if present
- Target distribution shape
- Sampling strategy needs

---

### 6. Correlation Analysis

**Goal:** Identify relationships between features

**Actions:**
```python
# Numeric correlations
corr_matrix = df[numeric_cols].corr()

# Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.show()

# High correlations
high_corr = np.where(np.abs(corr_matrix) > 0.8)
high_corr_pairs = [
    (corr_matrix.index[x], corr_matrix.columns[y], corr_matrix.iloc[x, y])
    for x, y in zip(*high_corr)
    if x != y and x < y
]
print("Highly correlated pairs:")
for pair in high_corr_pairs:
    print(f"  {pair[0]} & {pair[1]}: {pair[2]:.2f}")
```

**Checkpoint:**
- [ ] Highly correlated features identified
- [ ] Multicollinearity assessment complete

**Document:**
- Correlated feature pairs
- Features to potentially remove
- Interesting relationships

---

### 7. Target Correlations

**Goal:** Identify features related to target

**Actions:**
```python
# Correlation with target
target_corr = df[numeric_cols].corrwith(df[target_col]).sort_values(ascending=False)
print("Correlation with target:")
print(target_corr)

# Visualize top correlations
top_features = target_corr.abs().nlargest(10).index
for feat in top_features:
    if feat != target_col:
        plt.figure(figsize=(8, 6))
        plt.scatter(df[feat], df[target_col], alpha=0.5)
        plt.xlabel(feat)
        plt.ylabel(target_col)
        plt.title(f'{feat} vs {target_col}')
        plt.show()
```

**Checkpoint:**
- [ ] Top predictive features identified
- [ ] Relationship shapes understood (linear, nonlinear)

**Document:**
- Strongest predictors
- Non-linear relationships to engineer

---

### 8. Outlier Analysis

**Goal:** Identify and characterize outliers

**Actions:**
```python
# IQR method
def find_outliers_iqr(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    return len(outliers), lower, upper

for col in numeric_cols:
    n_outliers, lower, upper = find_outliers_iqr(df, col)
    if n_outliers > 0:
        print(f"{col}: {n_outliers} outliers ({n_outliers/len(df)*100:.1f}%)")
        print(f"  Bounds: [{lower:.2f}, {upper:.2f}]")
```

**Checkpoint:**
- [ ] Outlier extent quantified
- [ ] True outliers vs data errors distinguished
- [ ] Handling strategy determined

**Document:**
- Columns with significant outliers
- Outlier handling plan

---

### 9. Data Quality Summary

**Goal:** Synthesize findings into actionable summary

**Template:**
```markdown
## EDA Summary: [Dataset Name]

### Dataset Overview
- Rows: X
- Columns: Y
- Memory: Z MB

### Data Quality Issues
1. Missing data:
   - Column A: X% missing - [strategy]
   - Column B: Y% missing - [strategy]

2. Outliers:
   - Column C: X outliers - [strategy]

3. Data errors:
   - [Any errors found]

### Key Findings
1. Target is [balanced/imbalanced]
2. Top predictors: [list]
3. Correlated features to address: [list]

### Recommended Preprocessing
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Questions for Stakeholders
1. [Question about data]
2. [Question about business context]
```

---

## Common Issues

### Issue: Too Many Columns
**Solution:** Focus on subsets, use automated profiling tools like `pandas-profiling`

### Issue: Mixed Data Types
**Solution:** Handle each type separately, check for encoding issues

### Issue: Large Dataset
**Solution:** Sample for initial EDA, then verify findings on full data

---

## See Also

- **Parent**: [Workflows](README.md)
- **Next**: [Model Evaluation](model-evaluation.md)
- **Rules**: [Data Science Core](../../08-marketplace/catalog/rules-by-domain.md)
