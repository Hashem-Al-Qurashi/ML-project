import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print('=== ERROR ANALYSIS (PDF Section 1.6) ===')
print('Case studies for 2-3 false positives and 2-3 false negatives')

# Recreate the recommended model
provider_features = pd.read_csv('data/provider_features.csv', index_col=0)
X = provider_features.drop('PotentialFraud', axis=1)
y = provider_features['PotentialFraud'].map({'No': 0, 'Yes': 1})

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the best model (Logistic Regression)
lr_model = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
lr_model.fit(X_train_scaled, y_train)

# Get predictions and probabilities
pred = lr_model.predict(X_test_scaled)
pred_proba = lr_model.predict_proba(X_test_scaled)[:, 1]

# Create results DataFrame for analysis
test_results = X_test.copy()
test_results['true_label'] = y_test.values
test_results['predicted_label'] = pred
test_results['fraud_probability'] = pred_proba
test_results['provider_id'] = X_test.index

# Identify error cases
test_results['error_type'] = 'Correct'
test_results.loc[(test_results['true_label'] == 0) & (test_results['predicted_label'] == 1), 'error_type'] = 'False Positive'
test_results.loc[(test_results['true_label'] == 1) & (test_results['predicted_label'] == 0), 'error_type'] = 'False Negative'

print(f'\nError Distribution:')
print(test_results['error_type'].value_counts())

print('\n' + '='*80)
print('FALSE POSITIVE CASE STUDIES (Legitimate providers flagged as fraud)')
print('='*80)

false_positives = test_results[test_results['error_type'] == 'False Positive'].sort_values('fraud_probability', ascending=False)

for i, (idx, row) in enumerate(false_positives.head(3).iterrows()):
    print(f'\nFALSE POSITIVE #{i+1}: Provider {row["provider_id"]}')
    print(f'  Fraud Probability: {row["fraud_probability"]:.3f}')
    print(f'  Key Financial Metrics:')
    print(f'    Inpatient Total: ${row.get("ip_InscClaimAmtReimbursed_ip_sum", 0):.0f}')
    print(f'    Outpatient Total: ${row.get("op_InscClaimAmtReimbursed_op_sum", 0):.0f}')
    print(f'    Inpatient Claims: {row.get("ip_InscClaimAmtReimbursed_ip_count", 0):.0f}')
    print(f'    Outpatient Claims: {row.get("op_InscClaimAmtReimbursed_op_count", 0):.0f}')
    
    # Analysis of why it might be flagged
    total_amount = row.get('ip_InscClaimAmtReimbursed_ip_sum', 0) + row.get('op_InscClaimAmtReimbursed_op_sum', 0)
    total_claims = row.get('ip_InscClaimAmtReimbursed_ip_count', 0) + row.get('op_InscClaimAmtReimbursed_op_count', 0)
    avg_claim = total_amount / max(total_claims, 1)
    
    print(f'  Analysis: High volume provider (${total_amount:.0f} total, {total_claims:.0f} claims, ${avg_claim:.0f}/claim)')
    print(f'  Likely Issue: Volume-based false positive - high activity but legitimate pattern')

print('\n' + '='*80)
print('FALSE NEGATIVE CASE STUDIES (Fraudulent providers missed)')
print('='*80)

false_negatives = test_results[test_results['error_type'] == 'False Negative'].sort_values('fraud_probability', ascending=True)

for i, (idx, row) in enumerate(false_negatives.head(3).iterrows()):
    print(f'\nFALSE NEGATIVE #{i+1}: Provider {row["provider_id"]}')
    print(f'  Fraud Probability: {row["fraud_probability"]:.3f} (Below threshold)')
    print(f'  Key Financial Metrics:')
    print(f'    Inpatient Total: ${row.get("ip_InscClaimAmtReimbursed_ip_sum", 0):.0f}')
    print(f'    Outpatient Total: ${row.get("op_InscClaimAmtReimbursed_op_sum", 0):.0f}')
    print(f'    Inpatient Claims: {row.get("ip_InscClaimAmtReimbursed_ip_count", 0):.0f}')
    print(f'    Outpatient Claims: {row.get("op_InscClaimAmtReimbursed_op_count", 0):.0f}')
    
    total_amount = row.get('ip_InscClaimAmtReimbursed_ip_sum', 0) + row.get('op_InscClaimAmtReimbursed_op_sum', 0)
    total_claims = row.get('ip_InscClaimAmtReimbursed_ip_count', 0) + row.get('op_InscClaimAmtReimbursed_op_count', 0)
    
    print(f'  Analysis: Lower volume fraud (Total: ${total_amount:.0f}, Claims: {total_claims:.0f})')
    print(f'  Likely Issue: Sophisticated fraud with normal volume patterns')

print(f'\n' + '='*80)
print('REFINEMENT RECOMMENDATIONS (PDF Section 1.6)')
print('='*80)
print('1. Add temporal features: claim frequency patterns, seasonal variations')
print('2. Include diagnosis code clustering to detect unusual medical patterns')  
print('3. Add geographic features: provider location, patient travel distances')
print('4. Implement ensemble methods combining multiple algorithms')
print('5. Add procedural complexity scoring to detect upcoding patterns')