---
name: projectionlab
description: "Read financial projection data from ProjectionLab (app.projectionlab.com) via Chrome. Use this skill whenever the user mentions ProjectionLab, PL, financial projections, retirement plans, or wants to review/extract/validate data from their ProjectionLab plans — including plan settings, milestones, income, expenses, accounts, withdrawal strategies, growth rates, inflation, tax settings, drawdown order, Monte Carlo results, or current finances. Also trigger when the user wants to compare ProjectionLab assumptions against other documents, export PL data, or do a cross-check of projection inputs. Even if the user just says 'check my plan' or 'what are my projection assumptions', this skill should trigger if ProjectionLab is their projection tool."
---

# ProjectionLab Data Access Skill

This skill enables read-only access to ProjectionLab plans via the Chrome MCP. ProjectionLab is a Vue 3 single-page app that stores all plan data in Pinia state management stores, accessible through JavaScript execution in the browser.

## Prerequisites

Before using this skill, verify:
1. The Chrome MCP (Claude in Chrome) is connected
2. The user is logged into ProjectionLab in Chrome

If Chrome MCP is not connected or the user isn't logged in, tell the user what's needed and stop — don't attempt workarounds.

## How It Works

ProjectionLab runs on Vue 3 with Pinia for state management. All plan data — milestones, income, expenses, accounts, settings, variables — lives in Pinia stores accessible via JavaScript. The Chrome MCP's `javascript_tool` can read these stores directly, which is far more reliable and complete than scraping the UI visually.

## Step 1: Ensure ProjectionLab Is Open and Loaded

Navigate to ProjectionLab if not already there. If the user wants a specific plan, navigate to it.

```
Use mcp__Claude_in_Chrome__tabs_context_mcp to get current tabs.
If no tab is on app.projectionlab.com, navigate there.
Wait for the page to load, then take a screenshot to confirm the user is logged in.
```

If the page shows a login/signup screen, tell the user to log in and stop.

## Step 2: Access Pinia Stores

All data extraction uses this core pattern to get the Pinia instance:

```javascript
const app = document.querySelector('#app').__vue_app__;
let pinia = null;
for (const key of Object.getOwnPropertySymbols(app._context.provides)) {
  const val = app._context.provides[key];
  if (val && val._s) { pinia = val; break; }
}
// Now access any store:
// const planStore = pinia._s.get('plan');
// const currentFinances = pinia._s.get('current-finances');
```

### Available Pinia Stores

| Store | What it contains |
|-------|-----------------|
| `plan` | The currently loaded plan (milestones, income, expenses, accounts, assets, variables, withdrawal strategy) |
| `current-finances` | Current account balances and financial state |
| `monte-carlo` | Monte Carlo simulation results |
| `tax-analytics` | Tax projection analytics |
| `compare` | Plan comparison data |
| `plot` | Chart/plot data currently displayed |
| `settings` | App-level settings |
| `account` | User account info |
| `meta` | Plan metadata |

## Step 3: Extract the Requested Data

Choose the right extraction based on what the user needs. Always combine the Pinia access pattern from Step 2 with the specific extraction below. Keep JavaScript payloads focused — extract only what's needed and use `JSON.stringify()` to return structured data.

### Plan Overview

```javascript
const plan = pinia._s.get('plan').plan;
JSON.stringify({
  name: plan.name,
  id: plan.id,
  schema: plan.schema,
  lastUpdated: plan.lastUpdated,
  milestoneCount: plan.milestones?.length,
  incomeCount: plan.income?.events?.length,
  expenseCount: plan.expenses?.events?.length
}, null, 2);
```

### List All Plans

```javascript
const plans = pinia._s.get('plan').plans;
JSON.stringify(plans.map(p => ({
  name: p.name,
  id: p.id,
  lastUpdated: p.lastUpdated,
  icon: p.icon
})), null, 2);
```

### Plan Variables (Settings)

This is where growth rates, inflation, tax settings, allocation, and other key assumptions live.

```javascript
const vars = pinia._s.get('plan').plan.variables;
JSON.stringify(vars, null, 2);
```

Key fields in `variables`:
- `investmentReturn` — nominal equity return (%)
- `bondInvestmentReturn` — nominal bond return (%)
- `inflation` — inflation rate (%)
- `bondAllocation` — bond allocation curve (array of {x: year, y: %})
- `drawdownOrder` — account withdrawal priority (array of strings like "excess-cash", "taxable", "tfsa", "rrsp", "all-cash")
- `withholding` — tax withholding rates: `{taxDeferred, taxable, conversions}`
- `capGainsTaxablePercent` — capital gains inclusion rate (50% for Canada)
- `capGainsTaxAsIncome` — whether cap gains are taxed as income (true for Canada)
- `filingStatus` — tax filing status
- `flexSpending` — spending flexibility settings: `{enabled, scope, points, interpolation}`
- `estate` — estate planning parameters
- `investmentReturnCustom` — custom return curve if different from flat rate
- `inflationCustom` — custom inflation curve
- `dividendRateCustom` — custom dividend yield curve
- `cashFlowDefault` — what to do with surplus cash ("save", "spend", etc.)

### Milestones

```javascript
const milestones = pinia._s.get('plan').plan.milestones;
JSON.stringify(milestones.map(m => ({
  name: m.name,
  id: m.id,
  criteria: m.criteria,
  color: m.color
})), null, 2);
```

### Income Events

```javascript
const income = pinia._s.get('plan').plan.income.events;
JSON.stringify(income.map(e => ({
  name: e.name,
  id: e.id,
  type: e.type,
  amount: e.amount || e['initial-amount'],
  frequency: e.frequency,
  start: e.start,
  end: e.end,
  taxable: e.taxable,
  inflation: e.inflation
})), null, 2);
```

### Expense Events

```javascript
const expenses = pinia._s.get('plan').plan.expenses.events;
JSON.stringify(expenses.map(e => ({
  name: e.name,
  id: e.id,
  type: e.type,
  amount: e.amount || e['initial-amount'],
  frequency: e.frequency,
  start: e.start,
  end: e.end,
  essential: e.essential,
  inflation: e.inflation
})), null, 2);
```

### Accounts

```javascript
const accounts = pinia._s.get('plan').plan.accounts.events;
JSON.stringify(accounts.map(a => ({
  name: a.name,
  id: a.id,
  type: a.type,
  subtype: a.subtype,
  balance: a.balance,
  owner: a.owner,
  contributions: a.contributions,
  allocation: a.allocation
})), null, 2);
```

### Withdrawal Strategy

```javascript
const ws = pinia._s.get('plan').plan.withdrawalStrategy;
JSON.stringify(ws, null, 2);
```

### Assets

```javascript
const assets = pinia._s.get('plan').plan.assets.events;
JSON.stringify(assets.map(a => ({
  name: a.name,
  id: a.id,
  type: a.type,
  value: a.value,
  appreciation: a.appreciation
})), null, 2);
```

### Current Finances (Dashboard)

```javascript
const cf = pinia._s.get('current-finances').$state;
JSON.stringify(cf, null, 2);
```

### Full Plan Dump

When the user needs everything at once, extract the complete plan object. This can be large — warn the user and consider saving to a file rather than displaying inline.

```javascript
const plan = pinia._s.get('plan').plan;
JSON.stringify(plan, null, 2);
```

## Step 4: Navigate to a Specific Plan

If the user has multiple plans and wants a specific one, either:

1. **Click the plan on the dashboard** — navigate to the dashboard, find the plan card, click it
2. **Use the plan ID directly** — navigate to `https://app.projectionlab.com/plan/{planId}`

To find plan IDs:
```javascript
const plans = pinia._s.get('plan').plans;
JSON.stringify(plans.map(p => ({ name: p.name, id: p.id })));
```

## Export via JSON File

ProjectionLab also supports a full JSON export at `https://app.projectionlab.com/settings/export`. This exports ALL data (all plans, all accounts, all settings) as a downloadable JSON file. Use this when:
- The user wants a complete backup/snapshot
- You need to analyze data offline or save it to a file
- The data set is too large for inline JavaScript extraction

Navigate to the export page and describe the Export button to the user — downloading requires their confirmation.

## Important Notes

- **Read-only**: This skill only reads data. Never attempt to modify ProjectionLab data via JavaScript — it could corrupt the user's plans.
- **Data freshness**: The data reflects the current state of the loaded plan. If the user has unsaved changes in PL, those will be included. If they want the saved version, they should refresh PL first.
- **Large payloads**: Some plans have dozens of milestones, income events, etc. When extracting large datasets, consider extracting in parts or saving to a file rather than dumping everything into the conversation.
- **Schema changes**: ProjectionLab may update its internal data structures. If the JavaScript extraction fails or returns unexpected results, take a screenshot to verify the page state and try adjusting the extraction code.
- **Store availability**: Some stores (like `monte-carlo` or `tax-analytics`) only have data after the user has run those analyses in PL. Check if the store has meaningful data before presenting it.
