# Wallet Credit Scoring 
## Overview

This script processes DeFi transaction data from the Aave V2 protocol to generate a **credit score (0 to 1000)** for each wallet. Scores reflect how responsibly each wallet has interacted with the protocol.

---

## Input

* A JSON file of transaction-level data: `user-wallet-transactions.json`
* Each record includes:

  * `userWallet`, `action`, `amount`, `assetPriceUSD`, `timestamp`, etc.

## Actions Considered

* `deposit`: Adds capital to Aave
* `borrow`: Takes a loan
* `repay`: Pays back borrowed funds
* `redeemunderlying`: Withdraws deposits
* `liquidationcall`: Wallet was liquidated (risk event)

---

## Features Engineered Per Wallet

* Total USD amount of deposits, borrows, and repayments
* Count of each action (e.g., repay\_count, liquidation\_count)
* Number of unique active days on protocol
* Total number of transactions

---

## Scoring Heuristics

| Behavior                  | Effect on Score |
| ------------------------- | --------------- |
| Deposited > \$1,000       | +100            |
| Repaid loans (up to 100%) | +150 max        |
| Each liquidation          | -100 per event  |
| Active for up to 1 year   | +100 max        |
| Borrowed but never repaid | -150            |

* Final scores are clipped to range \[0, 1000]

---

## Output

* `wallet_credit_scores.json`: List of wallets with their credit scores:

```json
[
  {"wallet": "0xabc...", "credit_score": 780},
  {"wallet": "0xdef...", "credit_score": 450},
  ...
]
```

---

## How to Run

1. Ensure Python 3.8+ and `pandas` are installed.
2. Place `user-wallet-transactions.json` in the script directory.
3. Run the script:

```bash
python credit_score_generator.py
```

4. Check output: `wallet_credit_scores.json`

---

## Extensibility

This scoring model is intentionally simple and transparent. You can extend it with:

* Machine learning (e.g., XGBoost, logistic regression)
* Clustering of user behaviors
* Incorporating time-decay for older actions
* On-chain features like flashloan frequency, interaction with risky assets
