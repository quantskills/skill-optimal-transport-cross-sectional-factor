# Point-in-Time Reference

For signal date T, the reference contains only rows whose trading date is strictly earlier than T. The default is the latest `reference_window` valid dates, with `min_reference_dates` required before output becomes available.

The reference is a pooled weighted empirical distribution. Same-day-of-week or regime-conditioned references are exploratory variants and must be predeclared. Never use T, later dates, revised-without-vintage financial data, or post-event labels in the reference.

Store reference start/end, valid-date count, feature coverage, and availability status in diagnostics.
