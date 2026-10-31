# Analytics methodology

- **Missingness** is counted with Pandas `isna`; percentages are missing count / row count × 100.
- **Duplicate rows** are exact duplicate rows as recognized by Pandas `DataFrame.duplicated()` across all columns.
- **Unique values** exclude missing values.
- **Numeric summary** includes min, max, mean, median, sample standard deviation, and 25th/75th percentiles. Missing numeric values are ignored by the Pandas statistic methods.
- **Quality score** = `100 × (1 − missing_cells / total_cells) × (1 − duplicate_rows / max(rows, 1))`, clipped at zero. For zero-cell datasets, the current implementation returns 100. This is a transparent heuristic, not a universal quality standard; it weights missingness and exact duplicate-row prevalence equally in multiplicative form.
- **Categorical frequencies** are the top eight non-null values by frequency.
- **Sampling** is not used for accepted datasets in the current MVP. CSV/XLSX parsing is bounded to 500,000 rows and the upload size defaults to 10 MiB; results beyond the cap are not ingested. Larger datasets require asynchronous chunked processing and explicit approximate-statistics metadata.
- **Aggregations** use Pandas group-by with missing group labels retained. Metric aggregations are validated against numeric columns; count counts rows, distinct count requires a selected field. Results are sorted descending by value and capped at 500 groups.
- **Date parsing** is only performed when a user explicitly selects a date type transformation. Ambiguous date strings are not automatically reinterpreted.
- **Outliers, correlations, period comparisons, and trend lines** are not yet implemented as dedicated backend services. Add them with documented definitions and tests before presenting them as supported analysis.
