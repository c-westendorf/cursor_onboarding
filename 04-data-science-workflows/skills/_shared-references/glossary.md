# Data Science Glossary

Plain-language definitions for terms used across the skills library. Each entry explains what the term means, why it matters, and what to do when you see it.

---

## Missing Data Terms

### MCAR (Missing Completely At Random)
**What it means:** Data is missing for no reason at all — like a coin flip deciding which cells to erase.
**Why it matters:** If data is MCAR, simple methods (filling with the average) work fine.
**What to do:** Use median (numbers) or mode (categories) to fill missing values.

### MAR (Missing At Random)
**What it means:** Data is missing for a reason related to OTHER columns you can see. Example: younger people are less likely to report income — age predicts the missingness, not income itself.
**Why it matters:** You need smarter methods that use the relationship between columns.
**What to do:** Use IterativeImputer or KNNImputer — they leverage other columns to predict missing values.

### MNAR (Missing Not At Random)
**What it means:** Data is missing for a reason related to the MISSING VALUE ITSELF. Example: high-income people skip the income question because they don't want to reveal their income.
**Why it matters:** No statistical method can fully fix this. The missingness itself contains information.
**What to do:** Fill with a safe default (median/mode) AND create a `_was_missing` indicator column so models can learn from the missingness pattern.

---

## Feature Engineering Terms

### SULOV (Searching for Uncorrelated List of Variables)
**What it means:** A method that removes features that are highly correlated with each other (redundant copies). If Feature A and Feature B move together 90% of the time, you only need one.
**Why it matters:** Redundant features slow down models and can cause instability.
**What to do:** featurewiz runs this automatically. Adjust `corr_limit` (default 0.7) — lower values are more aggressive.

### MRMR (Maximum Relevance Minimum Redundancy)
**What it means:** After SULOV removes redundant features, MRMR ranks the remaining ones by how useful they are for predicting the target, while avoiding adding back redundancy.
**Why it matters:** Gives you the smallest set of features with the most predictive power.
**What to do:** featurewiz runs this automatically after SULOV.

### One-Hot Encoding
**What it means:** Converting a category column (like "Red", "Blue", "Green") into separate 0/1 columns — one for each category.
**Why it matters:** Most models need numbers, not text. This is the standard way to convert categories.
**What to do:** Used automatically for categorical columns with few unique values (<10-20).

### Target Encoding
**What it means:** Replacing each category with the average target value for that category. Example: if customers in "California" have average spend of $150, replace "California" with 150.
**Why it matters:** Works well for high-cardinality categories (many unique values like zip codes).
**What to do:** Must use fold-based encoding to prevent data leakage. Never fit on test data.

### Cyclical Encoding (sin/cos)
**What it means:** Converting circular features (hour of day, day of week, month) into sine and cosine values so the model understands that hour 23 is close to hour 0.
**Why it matters:** Without this, models think December (12) is far from January (1), when they're actually adjacent.
**What to do:** Applied automatically to datetime columns. Period is set based on the unit (24 for hours, 7 for days, 12 for months).

---

## Statistical Test Terms

### KS-test (Kolmogorov-Smirnov test)
**What it means:** Checks if two groups of numbers come from the same distribution (pattern). Like comparing the shape of two histograms.
**Why it matters:** Used to check if imputation changed the data distribution, or if production data drifted from training data.
**What to do:** p > 0.05 → distributions are similar (good). p < 0.05 → distributions differ (investigate). On very large datasets (>1M rows), always check effect size too — the test becomes overly sensitive.

### Chi-squared test
**What it means:** Checks if two categorical variables are related. Like asking: "Does knowing someone's city tell you anything about their purchase category?"
**Why it matters:** Identifies which categorical features are useful for prediction.
**What to do:** p < 0.05 → variables are related. Look at Cramer's V for the strength of the relationship.

### Cramer's V
**What it means:** Measures how strongly two categorical columns are related, on a scale from 0 (no relationship) to 1 (perfect relationship).
**Why it matters:** Unlike chi-squared, this tells you the STRENGTH, not just whether a relationship exists.
**What to do:** V > 0.3 → moderate relationship. V > 0.5 → strong relationship. V < 0.1 → negligible.

### Shapiro-Wilk test
**What it means:** Checks if your data follows a bell curve (normal distribution).
**Why it matters:** Some models and transformations assume normal data. If your data is skewed, you may need log or square root transforms.
**What to do:** p > 0.05 → data is approximately normal. p < 0.05 → data is not normal (consider transforms).

### ADF test (Augmented Dickey-Fuller)
**What it means:** Checks if a time-series has a stable average over time (is "stationary"). Like asking: "Is this trend going somewhere, or fluctuating around a constant?"
**Why it matters:** Most time-series models require stationary data. If your data has a trend, you need to remove it first.
**What to do:** p < 0.05 → data IS stationary (good). p > 0.05 → data is NOT stationary (apply differencing).

### Kruskal-Wallis test
**What it means:** Checks if a numeric feature differs significantly across groups (like checking if income differs across customer segments). Works even if data isn't normally distributed.
**Why it matters:** Identifies which numeric features are useful for classification tasks.
**What to do:** p < 0.05 → feature differs across groups (potentially useful). p > 0.05 → feature looks the same across groups.

### Mann-Whitney U test
**What it means:** Like Kruskal-Wallis, but specifically for comparing exactly 2 groups. Checks if one group tends to have higher values than the other.
**Why it matters:** Used for binary classification (e.g., churn vs. not churn) to identify important features.
**What to do:** Same interpretation as Kruskal-Wallis. p < 0.05 → significant difference.

---

## Data Quality Terms

### PSI (Population Stability Index)
**What it means:** Measures how much a feature's distribution has shifted between two time periods (e.g., training data vs. production data).
**Why it matters:** Large shifts mean your model may be making predictions on data it wasn't trained for.
**What to do:** PSI < 0.1 → no significant shift. PSI 0.1-0.2 → moderate shift (monitor). PSI > 0.2 → significant shift (investigate, consider retraining).

### Data Drift
**What it means:** The patterns in your data are changing over time. Example: customer behavior changed after a pandemic, but your model was trained on pre-pandemic data.
**Why it matters:** Models degrade when the data they see in production differs from training data.
**What to do:** Monitor key features with KS-test or PSI. Retrain when drift exceeds thresholds.

### Sentinel Values
**What it means:** Special placeholder values that represent "missing" but aren't technically null. Examples: -999, "N/A", "#REF!", "NULL", "not available".
**Why it matters:** They hide as real values and corrupt analysis (e.g., average income drops because of -999 entries).
**What to do:** Data-cleaning replaces all known sentinels with proper NaN values.

---

## EDA Terms

### Hopkins Statistic
**What it means:** Tests whether your data actually has natural groups (clusters) in it, or is just random noise with no structure.
**Why it matters:** If Hopkins is close to 0.5, clustering will find patterns that don't exist. Only cluster if Hopkins > 0.7.
**What to do:** H > 0.7 → data has cluster structure (proceed with clustering). H ≈ 0.5 → data is random (clustering is meaningless).

### VIF (Variance Inflation Factor)
**What it means:** Measures how much a feature's variability is inflated by its correlation with other features. High VIF = this feature is a near-duplicate of others.
**Why it matters:** High multicollinearity makes model coefficients unstable and uninterpretable.
**What to do:** VIF > 10 → serious multicollinearity (consider dropping). VIF > 5 → moderate (investigate).

### Skewness
**What it means:** Measures how lopsided a distribution is. Positive skew = long right tail (most values are low, a few are very high). Negative skew = long left tail.
**Why it matters:** Highly skewed features can hurt model performance. Log or square root transforms can fix this.
**What to do:** |skew| > 1 → consider log1p transform. |skew| > 2 → strongly recommend transform.

---

## Pipeline Terms

### Data Leakage
**What it means:** Accidentally using information from the future or from the test set during training. Like studying the answer key before an exam.
**Why it matters:** Your model looks great in testing but fails in production because it was "cheating."
**What to do:** ALWAYS fit transformers (scalers, encoders, imputers) on training data only. Apply `.transform()` to test data. Never look at test set statistics during feature engineering.

### Train/Test Split
**What it means:** Dividing your data into two parts: one for building the model (train) and one for evaluating it (test). Like practicing with some exam questions and being tested on others.
**Why it matters:** Without this, you can't tell if your model learned real patterns or just memorized the data.
**What to do:** Typical split: 80% train / 20% test. For time-series: use temporal split (train on past, test on future).

### Cross-Validation (CV)
**What it means:** Instead of one train/test split, you do multiple splits and average the results. Like taking 5 different exams instead of 1.
**Why it matters:** Gives a more reliable estimate of model performance than a single split.
**What to do:** Use 5-fold stratified CV for classification. Use time-series split for temporal data. Never use random CV for time-series.

### Feature Importance
**What it means:** A score showing how much each feature contributes to model predictions. High importance = this feature strongly influences the output.
**Why it matters:** Helps you understand what drives predictions and identify features that can be removed.
**What to do:** Check after training. Remove features with near-zero importance to simplify the model.
