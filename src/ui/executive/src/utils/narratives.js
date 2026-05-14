/**
 * Dashboard Narratives - Business-focused explanations
 * Designed for C-suite executives and operations managers
 */

export const NARRATIVES = {
  CYCLE_TIME_SAVINGS: {
    title: 'Cycle Time Savings',
    icon: '⏱️',
    content: `**What You're Seeing:**
This metric shows the operational efficiency gained through AI-enabled claims processing compared to traditional manual adjuster workflows.

**Industry Context:**
Traditional auto claims take an average of **19.3 days** from First Notice of Loss (FNOL) to settlement (industry baseline). With AI processing, eligible claims are being adjudicated in as little as **7-8 days**, representing a **60% cycle time reduction**.

**How It Works:**
- AI evaluates damage photos within minutes of submission
- Automated damage assessment eliminates back-and-forth with repair shops
- Straight-through processing (STP) for qualifying claims removes human touchpoints
- Only complex or high-value claims require adjuster review

**What the Numbers Mean:**
The "11.6 days saved" represents the average time reduction per AI-enabled claim. For a portfolio of 450,000 annual claims at 28% AI adoption (see AI Processed Claims chart), this translates to **1.5 million days** of cycle time eliminated system-wide.

**Business Impact:**
Faster cycle time = higher customer satisfaction (NPS improvement), reduced adjuster workload, and lower operational costs per claim (see Total Savings metric).`,
  },

  TOTAL_SAVINGS: {
    title: 'Total Savings',
    icon: '💰',
    content: `**What You're Seeing:**
This metric quantifies the direct operational cost savings from AI-enabled claims processing over the selected time period.

**Cost Structure:**
- **Traditional processing LAE:** $357.50 per claim (Acme current state: ~10% above $325 industry avg)
- **AI-enabled processing LAE:** $35.75-$107.25 per claim (auto-approved vs human review)
- **Net savings per claim:** $250-$322 depending on auto-adjudication rate

**Calculation Method:**
Total Savings = (AI-enabled claims × $357.50 baseline) - (Actual AI operational costs)

The dashboard shows LAE savings over 6 months across 4,500 sample claims (representing 1% of actual volume). At full production scale (450,000 claims), this projects to approximately **$16M in annual LAE savings** (6-month cumulative with phased rollout). At Week 42 steady-state run-rate, annual savings reach **$26M**.

**Why This Matters:**
- Direct impact on loss adjustment expense (LAE) ratio
- Redeployment opportunity: freed adjuster capacity can focus on complex claims, fraud investigation, or customer service escalations
- ROI justification for AI platform investment (typical payback period: 8-14 months)

**Cross-Reference:**
See the Auto-Adjudication Rate metric to understand the driver of these savings. Higher auto-adjudication = lower human review costs = greater savings.`,
  },

  AUTO_ADJUDICATION_RATE: {
    title: 'Auto-Adjudication Rate',
    icon: '🎯',
    content: `**What You're Seeing:**
This metric measures the percentage of AI-enabled claims that are fully adjudicated without any human intervention—true straight-through processing (STP).

**The Number:**
**70.6%** means that 7 out of 10 AI-enabled claims are auto-approved from FNOL to settlement with zero adjuster touchpoints.

**How We Got Here:**
- **Oct 2025 (Month 1):** 2.9% auto-adjudication, $4,000 confidence threshold
- **Mar 2026 (Month 6):** 59.6% auto-adjudication, $6,500 confidence threshold
- Progressive threshold increases as AI model accuracy improved and business confidence grew

**What Drives This Rate:**
1. **AI Confidence Score** - Model must exceed 0.85 confidence threshold
2. **Claim Amount** - Must fall below monthly threshold ($4K-$6.5K progression)
3. **Fraud Risk** - Fraud detection score must be below 0.7
4. **Customer Opt-In** - 50% of eligible customers have opted into AI processing (Pilot target)

**Industry Comparison:**
Leading insurers achieve 50-65% auto-adjudication for AI-eligible claims. This portfolio is performing **above industry benchmark**.

**The Other 29.4%:**
These AI-enabled claims still get AI assessment but require one human review due to:
- High claim value (>threshold)
- Low AI confidence (<0.85)
- Elevated fraud risk
- Customer appeal requests

See the AI Processed Claims chart for the full processing path breakdown.`,
  },

  AI_PROCESSED_CLAIMS: {
    title: 'AI Processed Claims',
    icon: '🥧',
    content: `**What You're Seeing:**
This pie chart shows how all claims in the portfolio are distributed across three processing paths.

**The Three Categories:**

**1. Traditional Processing (~81%)**
Claims that go through standard manual adjuster workflows:
- **65%** - Internal/mechanical damage (NOT eligible for AI—requires physical inspection)
- **7%** - Body damage but customer declined AI processing
- **9%** - Body damage but not yet onboarded to AI

**2. AI Auto-Approved (~12%)**
Body damage claims with full straight-through processing (STP):
- Photos analyzed by AI within minutes
- Damage and cost estimated automatically
- Settlement issued without human review
- Average cycle time: 2-4 days

**3. AI + Human Review (~7%)**
Body damage claims that receive AI assessment plus one adjuster review:
- AI provides initial estimate and risk score
- Adjuster validates or adjusts
- Triggered by: high value, low confidence, customer appeal
- Average cycle time: 5-8 days (still 60% faster than traditional)

**Why Only 17.5% AI Adoption?**
Two key constraints limit AI eligibility:
1. **Damage Type:** Only 35% of claims are body damage (industry data)
2. **Customer Opt-In:** 50% opt-in rate among eligible customers (Pilot target)
3. **Result:** 35% × 50% = 17.5% maximum AI adoption rate (Pilot)

**Business Strategy:**
Focus on maximizing auto-adjudication rate within the 28% eligible population rather than forcing AI onto ineligible claim types.`,
  },

  TREND_CHART_CYCLE_TIME: {
    title: 'Cycle Time Savings Trend',
    icon: '📈',
    content: `**What You're Seeing:**
This chart shows how cycle time savings have improved month-over-month as AI processing matured.

**Reading the Chart:**
- **Y-axis:** Days saved per AI-enabled claim (compared to 19.3-day baseline)
- **X-axis:** 6-month timeline (Oct 2025 - Mar 2026)
- **Trend:** Progressive improvement from 6.9 days saved to 10.4+ days saved

**Why The Improvement?**
1. **Model Training** - AI accuracy improved with each month's data
2. **Process Optimization** - Repair shop integrations reduced delays
3. **Threshold Tuning** - Confidence thresholds calibrated for speed vs accuracy
4. **Adoption Curve** - More adjusters gained confidence in AI recommendations

**What to Watch:**
- **Plateau Point:** Most AI implementations plateau at 11-13 days saved
- **Seasonal Factors:** Winter months (Jan-Mar) often show higher savings due to simpler weather-related claims
- **Target:** Industry leaders achieve 14-15 days saved (marked on KPI card)

**Correlation:**
Compare this trend to the Auto-Adjudication Rate trend—higher auto-adjudication directly drives cycle time reduction.`,
  },

  TREND_CHART_TOTAL_SAVINGS: {
    title: 'Total Savings Trend',
    icon: '💵',
    content: `**What You're Seeing:**
This chart tracks cumulative monthly operational cost savings from AI processing.

**Reading the Chart:**
- **Y-axis:** Dollar savings per month (operational costs avoided)
- **X-axis:** 6-month timeline (Oct 2025 - Mar 2026)
- **Growth:** From $9,836/month (Oct) to $61,041/month (Mar)

**Why Savings Accelerated:**
1. **Volume Growth** - More claims routed to AI each month (adoption ramping)
2. **Efficiency Gains** - Higher auto-adjudication rate = lower per-claim cost
3. **Threshold Increases** - Larger claims auto-approved as confidence grew
4. **Scale Economics** - Fixed AI infrastructure costs amortized across more claims

**Monthly Breakdown:**
- **Oct-Dec 2025:** Early stage, limited adoption, proving value
- **Jan-Feb 2026:** Rapid scaling, adjuster buy-in, process refinement
- **Mar 2026:** Mature operation, peak efficiency

**Extrapolation:**
The dashboard shows 1% sample data. At full production scale (100×), March's $61K becomes **$6.1M monthly savings** or **$73M annualized**. See the Extrapolation card in the right sidebar for portfolio-level projections.

**ROI Context:**
Typical AI claims platform investment: $5-8M. At this savings trajectory, payback achieved in 10-12 months.`,
  },

  TREND_CHART_AUTO_ADJ: {
    title: 'Auto-Adjudication Rate Trend',
    icon: '🎚️',
    content: `**What You're Seeing:**
This chart tracks the percentage of AI-enabled claims achieving true straight-through processing (STP) without human touchpoints.

**Reading the Chart:**
- **Y-axis:** Auto-adjudication rate (% of AI-enabled claims)
- **X-axis:** 6-month timeline (Oct 2025 - Mar 2026)
- **Progressive Growth:** 2.9% → 59.6% (20x improvement)

**The Journey:**
- **Month 1-2 (Oct-Nov):** Conservative thresholds, building confidence, <10% auto-adj
- **Month 3-4 (Dec-Jan):** Threshold increases, adjuster training, rapid climb to 40%+
- **Month 5-6 (Feb-Mar):** Mature operation, fine-tuning, stabilizing at 50-60%

**What Limits the Rate:**
Even with perfect AI accuracy, 100% auto-adjudication is unrealistic due to:
- High-value claims requiring oversight (>$6,500)
- Low-confidence predictions (model uncertainty)
- Fraud detection triggers (suspicious patterns)
- Customer appeals and special requests

**Industry Benchmark:**
- **Best-in-class:** 60-70% auto-adjudication
- **Average:** 35-50% auto-adjudication
- **This portfolio:** 59.6% (above average, approaching best-in-class)

**Business Implication:**
Every 10% increase in auto-adjudication rate reduces LAE by approximately $3-5M annually at full scale. The Mar 2026 rate (59.6%) represents a **$25-30M annual LAE reduction** compared to traditional processing.`,
  },

  QUERY_INTERFACE: {
    title: 'Query Interface',
    icon: '🔍',
    content: `**What You're Seeing:**
A flexible query tool to explore the claims data behind the dashboard metrics.

**Two Ways to Query:**

**1. Preset Queries (Dropdown)**
Pre-built business questions with optimized SQL:
- **Top 10 Highest Savings Claims** - Identify where AI delivered maximum value
- **Claims Requiring Human Review** - Analyze why auto-adjudication failed
- **Fraud Detection Analysis** - Review flagged claims and detection accuracy
- **Monthly Performance Comparison** - Period-over-period trending

**2. Custom Queries (Text Input)**
Natural language questions converted to SQL (Phase 5 feature):
- "Show me all claims over $5,000 that were auto-adjudicated"
- "What's the average cycle time by month for traditional claims?"
- "How many fraud cases were detected in Q1 2026?"

**How to Use:**
1. Select a preset query from the dropdown OR type a custom question
2. Click "Generate Report"
3. Results appear below in tabular format
4. Click individual claim IDs to drill into full claim details

**Data Scope:**
Queries run against the full 6-month dataset (4,500 sample claims). All dollar amounts and volumes shown are at 1% sample scale—see the Demo Data Disclaimer for extrapolation methodology.

**Pro Tip:**
Use preset queries as templates to understand what data is available, then adapt them to your specific business questions.`,
  },
};
