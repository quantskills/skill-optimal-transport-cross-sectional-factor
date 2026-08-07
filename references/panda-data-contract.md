# PandaData Contract

The direct runtime reference is `skill-pandadata-api` and its versioned method index. This Skill does not copy API implementation and does not require MCP.

A first implementation may consume normalized results from `get_stock_daily` and a separately verified point-in-time feature source. `get_fina_reports`, `get_fina_forecast`, `get_stock_market_event`, `get_stock_financial_event`, and `get_fund_etf_constituents` are documented methods, but a formal factor run must verify returned fields and disclosure availability for the selected account/version. Undocumented or `not exported` methods are blocked, not guessed.

Record SDK version, query parameters, returned schema, retrieval time, availability date, and dataset fingerprint. No credential handling is performed here.
