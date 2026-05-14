# Rules to generate the synthetic data


## Fraudulent auto claims
* Industry average of fraudulent auto claims = 15%  (Reference : https://www.insurancejournal.com/news/national/2015/02/04/356392.htm)
    * Target for identifying fraud = 50% of (Total auto adjudicated claims * 0.15)
    * Potential number of fraudulent claims = 0.15 * total claims
* Number of claims per quarter = 200000
* Average industry cycle time = 19.3 days  (Refer: https://www.autobodynews.com/news/auto-insurance-customer-satisfaction-strained-by-higher-deductibles-more-total-losses)

## Cost savings from auto adjudication
* Operational cost of processing a claim
    * Straight-Through Processing (STP): Less than $20. Fully automated, AI-driven claims (like immediate glass replacement or minor comprehensive windshield damage) require zero human touchpoints, drastically lowering the unit cost.
    * Standard Collision/Property Claims: $200 – $450. Requires a human adjuster to review photos or visit a repair shop, verify policy logic, coordinate a rental vehicle, and approve the supplement invoices.

    Saving factor = (1 - 20/300) = 0.93% Let's say the saving is 0.9 on auto-adjudicated claims
    Saving factor with auto adjudication with 1 human review = 0.85


## The samples in the synthetic data MUST have the following sample types


Average claim loss = 6000

---Month----|---Number of claims ---|---Auto adjudication threshold---|-------Auto adjudicated----------|-------Fraud-----------------------------|---Fraud detected---|
Oct 2025        75000                   4000                              claim amount < threshold              15% of auto adjudicated claims        40%
Nov 2025        75000                   4500                              claim amount < threshold              15% of auto adjudicated claims        50%
Dec 2025        75000                   5000                              claim amount < threshold              15% of auto adjudicated claims        60%
Jan 2026        75000                   5500                              claim amount < threshold              15% of auto adjudicated claims        70%
Feb 2026        75000                   6000                              claim amount < threshold              15% of auto adjudicated claims        80%
Mar 2026        75000                   6500                              claim amount < threshold              15% of auto adjudicated claims        85%


* Total number will 1% of the actual claims e.g., if in a month there are 75000 claims, the sample for that month will be 750
* The results on the dashboard will be extrapolated