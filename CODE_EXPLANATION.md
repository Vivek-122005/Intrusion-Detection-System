# Complete Code Explanation: Intrusion Detection System (IDS)

## Project Overview
This project builds a Machine Learning-Based Intrusion Detection System that classifies network traffic into 15 categories (1 benign + 14 attack types) using the CSE-CIC-IDS2018 dataset.

---

## 📚 **Section 1: Package Installation & Setup**

### Cell 0: Install Dependencies
```python
%pip install -q imbalanced-learn scikit-learn seaborn
```
**Purpose**: Installs essential libraries:
- **imbalanced-learn**: For handling class imbalance (SMOTE)
- **scikit-learn**: Core ML algorithms and utilities
- **seaborn**: For visualizations

---

## 📚 **Section 2: Helper Functions (Cell 1)**

### Constants
```python
RANDOM_STATE = 42          # Ensures reproducible results
NUMERIC_NA_FILL = 0.0      # Default value for missing numbers
EXCLUDE_COLS = {...}       # Columns to drop (IPs, IDs, timestamps)
```

### Function 1: `reduce_memory_usage()`
**Purpose**: Reduces memory footprint by converting:
- `float64` → `float32` (half precision)
- `int64` → `int32` (half precision)

**Why**: Large datasets (6.6M rows) need memory optimization. This reduces RAM usage by ~50%.

### Function 2: `clean_columns()`
**Purpose**: 
- Removes non-feature columns (IPs, Flow IDs, Timestamps)
- Standardizes label column name to 'Label'
- Prepares data for ML

### Function 3: `coerce_numeric()`
**Purpose**: Converts string numbers to numeric types automatically
- Handles cases where data was saved as strings
- Uses `errors='coerce'` to handle invalid values

### Function 4: `load_parquet_files()`
**Purpose**: Main data loading function
1. Loads multiple parquet files sequentially
2. Cleans each file
3. Concatenates into one dataframe
4. Handles memory with `gc.collect()`
5. Replaces infinite values and NaNs with 0.0
6. Returns cleaned dataframe

**Memory Management**: Uses `gc.collect()` after each file to prevent RAM overflow.

### Function 5: `select_features()`
**Purpose**: Separates features (X) from labels (y)
- Keeps only numeric columns as features
- Returns tuple: (features DataFrame, labels Series)

---

## 📚 **Section 3: Data Loading & Preparation (Cell 2)**

### Dataset Information
- **Source**: CSE-CIC-IDS2018 (10 parquet files)
- **Total Samples**: 6,659,532 rows
- **Features**: 77 numeric columns
- **Classes**: 15 categories

### Workflow:
1. **Define file paths**: Lists all 10 attack scenario files
2. **Load data**: Calls `load_parquet_files()` to combine all files
3. **Extract features**: Separates X (features) and y (labels)
4. **Label encoding**: Converts string labels to numbers (0-14)
   - Example: "Benign" → 0, "Bot" → 1, etc.

### Output:
```
✅ Combined dataset: (6659532, 78)
✅ Encoded 15 classes: 0=Benign, 1=Bot, 2=Brute Force -Web, ...
```

---

## 📚 **Section 4: Data Balancing (Cell 3)**

### Problem: Class Imbalance
- **Benign**: 4,994,160 samples (75%)
- **Attack classes**: Range from 53 to 575,364 samples
- **Issue**: Models favor majority class (Benign)

### Solution Strategy:
1. **Downsampling**: Cap each class to 10,000 samples max
2. **SMOTE**: Oversample minority classes during training only
3. **Stratified Split**: Maintain class distribution in train/test

### Code Breakdown:
```python
max_samples_per_class = 10000
# For each class, sample at most 10,000 rows
balanced_df = tmp_df.groupby('Label_encoded').apply(
    lambda x: x.sample(min(len(x), max_samples_per_class))
)
```

### Train/Test Split:
- **80% training** (74,102 samples)
- **20% testing** (18,526 samples)
- **Stratified**: Maintains class proportions

---

## 📚 **Section 5: Baseline Model Training (Cell 4)**

### Three Models Tested:

#### 1. **Logistic Regression** (`logreg_saga`)
- **Algorithm**: Linear classifier
- **Pipeline**: SMOTE → StandardScaler → LogisticRegression
- **Why Scaler**: LR is sensitive to feature scales
- **Class Weight**: 'balanced' (handles imbalance)
- **Solver**: 'saga' (handles large datasets)

#### 2. **Random Forest** (`random_forest`)
- **Algorithm**: Ensemble of decision trees
- **Pipeline**: SMOTE → RandomForest
- **No Scaler**: Trees don't need scaling
- **Trees**: 300 estimators
- **Class Weight**: 'balanced_subsample'

#### 3. **HistGradientBoosting** (`hist_gb`)
- **Algorithm**: Gradient boosting (memory-efficient)
- **Pipeline**: SMOTE → HistGradientBoosting
- **No Scaler**: Tree-based, scale-invariant
- **Parameters**: learning_rate=0.1, max_leaf_nodes=31

### Training Process:
```python
for each model:
    1. Create pipeline with SMOTE + Model
    2. Fit on training data (SMOTE applied only to train)
    3. Predict on test data
    4. Calculate macro F1-score
    5. Store results
```

### Evaluation Metric: **Macro F1-Score**
- **Why**: Handles imbalanced classes better than accuracy
- **Formula**: Average F1 across all classes (gives equal weight)

### Results:
- **Logistic Regression**: F1 = 0.6500
- **Random Forest**: F1 = 0.7985
- **HistGradientBoosting**: F1 = 0.8193 ✅ **Winner**

### Best Model Selection:
The code automatically selects the model with highest macro F1-score:
```python
best_name = max(results, key=lambda k: results[k]['macro_f1'])
```

---

## 📚 **Section 6: Model Persistence (Original Cell 5)**

Saves the best model and label encoder for later use.

---

## 📚 **Section 7: Advanced Improvements**

### Cell 6: Class-Dependent Sample Caps
**Problem**: Fixed 10k cap doesn't reflect class rarity

**Solution**: Proportional caps based on class frequency
```python
target_total = 150_000  # Total samples budget
# Use sqrt of frequency to give more weight to rare classes
proportions = sqrt(class_counts / sum(class_counts))
per_class_caps = proportions * target_total
```

**Result**: Better balance - rare classes get at least 2,000 samples each.

---

### Cell 7: Feature Selection (Mutual Information)

**Problem**: 77 features may include noise/redundancy

**Solution**: Select top-k features using Mutual Information
```python
mi = mutual_info_classif(X_train, y_train)
selected_features = top 60 features by MI score
```

**Why MI**: Measures dependency between features and labels
- Higher MI = more predictive feature
- Reduces overfitting, speeds up training

**Result**: Top 60 features selected, baseline F1 = 0.8237

---

### Cell 8: SMOTE-NC (Nominal Categorical)

**Problem**: Some integer features are categorical (Protocol, Flags)

**Solution**: SMOTE-NC handles mixed data types
```python
# Detect categorical-like integers (≤10 unique values)
cat_like = [cols with ≤10 unique values]
sampler = SMOTENC(categorical_features=cat_idx)
```

**Result**: Better synthetic sample generation, F1 = 0.8253

---

### Cell 9: Hyperparameter Tuning

**Problem**: Default parameters may not be optimal

**Solution**: Randomized search over parameter space
```python
param_distributions = {
    'learning_rate': uniform(0.03, 0.2),
    'max_leaf_nodes': randint(15, 63),
    'max_depth': randint(3, 20),
    'min_samples_leaf': randint(10, 200)
}
```

**Process**:
1. Try 20 random combinations
2. 3-fold cross-validation
3. Select best by macro F1
4. **Best CV Score**: 0.8254
5. **Test Score**: 0.8196

**Best Parameters Found**:
- learning_rate: 0.135
- max_depth: 12
- max_leaf_nodes: 42
- min_samples_leaf: 197

---

## 📚 **Section 8: Comprehensive Model Saving (Cell 10)**

### What Gets Saved:

1. **Model File**: `ids_tuned_hist_gb.joblib`
   - The trained pipeline (SMOTE + HistGradientBoosting)

2. **Label Encoder**: `label_encoder.joblib`
   - Maps class numbers ↔ class names
   - Needed to decode predictions

3. **Selected Features**: `selected_features.json`
   - List of 60 feature names
   - Ensures same features used in inference

4. **Metadata**: `model_metadata.json`
   - Model info (type, params, scores, classes)
   - For documentation and tracking

### Storage Locations:
- `artifacts/` (project root)
- `backend/models/` (for Flask API)

**Why Both**: Allows easy access for notebook experiments and web app deployment.

---

## 📚 **Section 9: Additional Dataset Download Cells**

### Cell 11-13: Kaggle Dataset Download
- Downloads CSE-CIC-IDS2018 dataset via Kaggle API
- Extracts to cache directory
- Lists available files

**Note**: These were early data acquisition steps, now consolidated in main workflow.

---

## 📚 **Section 10: Alternative Processing Cells**

### Cells 14-18: Alternate Data Processing Path
Some cells show alternative approaches:
- Direct pandas loading
- Different cleaning strategies
- Label encoding variations

**Status**: These were experimental/debugging cells. Main workflow uses Cells 1-10.

---

## 🔄 **Complete Workflow Summary**

```
1. Install Packages
   ↓
2. Define Helper Functions
   ↓
3. Load & Combine 10 Parquet Files (6.6M rows)
   ↓
4. Encode Labels (15 classes)
   ↓
5. Balance Dataset (cap per class)
   ↓
6. Split Train/Test (80/20, stratified)
   ↓
7. Train 3 Baseline Models
   ↓
8. Select Best Model (HistGradientBoosting)
   ↓
9. [OPTIONAL] Advanced: Feature Selection
   ↓
10. [OPTIONAL] Advanced: SMOTE-NC
    ↓
11. [OPTIONAL] Advanced: Hyperparameter Tuning
    ↓
12. Save Model + Artifacts
```

---

## 🎯 **Key Design Decisions**

### 1. **Memory Management**
- Downsampling from 6.6M → 150K samples
- Type conversion (float64→float32)
- Garbage collection between steps

### 2. **Class Imbalance Handling**
- **Downsampling**: Reduces majority class dominance
- **SMOTE**: Synthesizes minority class samples
- **Class Weights**: Built-in model parameters

### 3. **Pipeline Architecture**
- SMOTE applied **only during training**
- Prevents data leakage to test set
- Ensures fair evaluation

### 4. **Feature Engineering**
- Mutual Information for selection
- Removes 17 redundant features
- Improves speed and accuracy

### 5. **Model Selection**
- Macro F1-score (better than accuracy for imbalance)
- Cross-validation for tuning
- Separate test set for final evaluation

---

## 📊 **Final Model Performance**

- **Model**: Tuned HistGradientBoosting
- **CV Macro F1**: 0.8254 (82.54%)
- **Test Macro F1**: 0.8196 (81.96%)
- **Features**: 60 (selected from 77)
- **Classes**: 15 (1 benign + 14 attacks)

---

## 🔧 **How to Use This Code**

1. **Run cells sequentially** (Cell 0 → Cell 10)
2. **Adjust parameters**:
   - `max_samples_per_class`: Increase for better accuracy (more RAM)
   - `top_k`: Change number of selected features
   - `n_iter`: More tuning iterations = better results

3. **Model is saved** automatically after Cell 10
4. **Use saved model** in Flask backend for web predictions

---

## 💡 **Why Each Step Matters**

- **Memory optimization**: Enables training on limited RAM
- **Class balancing**: Prevents model bias toward majority class
- **Feature selection**: Reduces noise, improves generalization
- **Hyperparameter tuning**: Extracts maximum performance
- **Proper evaluation**: Ensures model works on unseen data

This codebase represents a production-ready IDS pipeline with proper ML practices! 🚀



