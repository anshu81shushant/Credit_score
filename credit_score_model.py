import json
import pandas as pd
from datetime import datetime
import numpy as np

# Load JSON data
with open("user-wallet-transactions.json") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Normalize nested fields
df['amount'] = df['actionData'].apply(lambda x: float(x.get('amount', 0)))
df['assetPriceUSD'] = df['actionData'].apply(lambda x: float(x.get('assetPriceUSD', 0)))
df['usd_value'] = df['amount'] * df['assetPriceUSD']
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Feature Engineering
grouped = df.groupby('userWallet')

features = pd.DataFrame(index=grouped.groups.keys())

features['total_deposit_usd'] = grouped.apply(lambda x: x[x.action == 'deposit'].usd_value.sum())
features['total_borrow_usd'] = grouped.apply(lambda x: x[x.action == 'borrow'].usd_value.sum())
features['total_repay_usd'] = grouped.apply(lambda x: x[x.action == 'repay'].usd_value.sum())
features['redeem_count'] = grouped.apply(lambda x: (x.action == 'redeemunderlying').sum())
features['liquidation_count'] = grouped.apply(lambda x: (x.action == 'liquidationcall').sum())
features['borrow_count'] = grouped.apply(lambda x: (x.action == 'borrow').sum())
features['repay_count'] = grouped.apply(lambda x: (x.action == 'repay').sum())
features['active_days'] = grouped.timestamp.agg(lambda x: (x.max() - x.min()).days + 1)
features['tx_count'] = grouped.size()

# Replace NaN with 0
features = features.fillna(0)


# Scoring Heuristic
def compute_score(row):
    score = 500

    # Reward healthy activity
    if row.total_deposit_usd > 1000:
        score += 100
    if row.total_repay_usd > 0 and row.total_borrow_usd > 0:
        repay_ratio = row.total_repay_usd / row.total_borrow_usd
        score += min(repay_ratio, 1.0) * 150

    # Penalize liquidations
    score -= row.liquidation_count * 100

    # Reward active time
    score += min(row.active_days / 365, 1) * 100

    # Penalize high borrow with no repay
    if row.total_borrow_usd > 0 and row.total_repay_usd == 0:
        score -= 150

    return int(np.clip(score, 0, 1000))


features['credit_score'] = features.apply(compute_score, axis=1)

# Output as JSON
output = features['credit_score'].reset_index().rename(columns={'userWallet': 'wallet'})
output_json = output.to_dict(orient='records')

with open("wallet_credit_scores.json", "w") as f:
    json.dump(output_json, f, indent=2)

print("✅ Wallet credit scores saved to 'wallet_credit_scores.json'")
