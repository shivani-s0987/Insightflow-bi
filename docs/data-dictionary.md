# Data dictionary

## Synthetic demo: E-commerce Orders

| Column | Type | Meaning |
|---|---|---|
| order_id | string | Synthetic unique order identifier |
| order_date | ISO date | Synthetic order date |
| customer_id | string | Synthetic customer key |
| category | category | Product category |
| region | category | Sales region |
| quantity | integer | Units in order |
| unit_price | decimal | Synthetic price per unit in USD |
| revenue | decimal | quantity × unit_price; synthetic order amount |
| status | category | completed, returned, or pending |

## Synthetic demo: Marketing Performance

`campaign_id`, `date`, `channel`, `region`, `spend`, `clicks`, `conversions`, `cost_per_conversion`. Spend is synthetic USD; cost per conversion uses a denominator floor of one so the generated field remains defined even for zero conversions. Treat it as a demonstration field, not a finance-grade cost measure.

## Synthetic demo: Customer Support Operations

`ticket_id`, `date`, `issue_type`, `channel`, `priority`, `resolution_minutes`, `status`, `satisfaction`. Resolution time and satisfaction values are synthetic; satisfaction is a 1–5 integer.

All demo data is generated deterministically by `seed_demo`; it does not represent real customers, companies, or business results.
