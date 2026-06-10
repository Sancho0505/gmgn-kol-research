CREATE TABLE IF NOT EXISTS tokens (
    id BIGSERIAL PRIMARY KEY,
    chain TEXT NOT NULL DEFAULT 'sol',
    token_address TEXT NOT NULL UNIQUE,
    symbol TEXT,
    name TEXT,
    discovered_at TIMESTAMPTZ NOT NULL,
    creation_timestamp TIMESTAMPTZ,
    open_timestamp TIMESTAMPTZ,
    launchpad_platform TEXT,
    launchpad_status TEXT,
    raw_discovery_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS token_snapshots (
    id BIGSERIAL PRIMARY KEY,
    token_id BIGINT NOT NULL REFERENCES tokens(id) ON DELETE CASCADE,
    snapshot_at TIMESTAMPTZ NOT NULL,
    snapshot_window TEXT NOT NULL,
    price_usd NUMERIC,
    market_cap NUMERIC,
    liquidity NUMERIC,
    holder_count INTEGER,
    volume_1m NUMERIC,
    volume_5m NUMERIC,
    volume_1h NUMERIC,
    buys_1m INTEGER,
    sells_1m INTEGER,
    buys_5m INTEGER,
    sells_5m INTEGER,
    swaps_1m INTEGER,
    swaps_5m INTEGER,
    smart_wallet_count INTEGER,
    renowned_wallet_count INTEGER,
    sniper_wallet_count INTEGER,
    bundler_wallet_count INTEGER,
    rat_trader_wallet_count INTEGER,
    fresh_wallet_count INTEGER,
    rug_ratio NUMERIC,
    is_wash_trading BOOLEAN,
    top_10_holder_rate NUMERIC,
    creator_balance_rate NUMERIC,
    creator_token_status TEXT,
    rat_trader_amount_rate NUMERIC,
    bundler_trader_amount_rate NUMERIC,
    sniper_count INTEGER,
    raw_info_json JSONB,
    raw_security_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS token_traders (
    id BIGSERIAL PRIMARY KEY,
    token_id BIGINT NOT NULL REFERENCES tokens(id) ON DELETE CASCADE,
    observed_at TIMESTAMPTZ NOT NULL,
    wallet_address TEXT NOT NULL,
    rank INTEGER,
    tags TEXT[],
    maker_token_tags TEXT[],
    is_smart_wallet BOOLEAN NOT NULL DEFAULT FALSE,
    is_renowned BOOLEAN NOT NULL DEFAULT FALSE,
    is_sniper BOOLEAN NOT NULL DEFAULT FALSE,
    is_bundler BOOLEAN NOT NULL DEFAULT FALSE,
    is_rat_trader BOOLEAN NOT NULL DEFAULT FALSE,
    is_fresh_wallet BOOLEAN NOT NULL DEFAULT FALSE,
    buy_volume_cur NUMERIC,
    sell_volume_cur NUMERIC,
    buy_tx_count_cur INTEGER,
    sell_tx_count_cur INTEGER,
    amount_percentage NUMERIC,
    realized_profit NUMERIC,
    unrealized_profit NUMERIC,
    realized_pnl NUMERIC,
    unrealized_pnl NUMERIC,
    start_holding_at TIMESTAMPTZ,
    last_active_timestamp TIMESTAMPTZ,
    wallet_created_at TIMESTAMPTZ,
    funding_source_address TEXT,
    raw_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kol_accounts (
    id BIGSERIAL PRIMARY KEY,
    x_user_id TEXT UNIQUE,
    handle TEXT NOT NULL UNIQUE,
    display_name TEXT,
    category TEXT,
    follower_count BIGINT,
    baseline_engagement_rate NUMERIC,
    tier TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kol_posts (
    id BIGSERIAL PRIMARY KEY,
    x_post_id TEXT NOT NULL UNIQUE,
    kol_account_id BIGINT NOT NULL REFERENCES kol_accounts(id) ON DELETE CASCADE,
    posted_at TIMESTAMPTZ NOT NULL,
    text TEXT NOT NULL,
    mentioned_contracts TEXT[],
    mentioned_tickers TEXT[],
    mentioned_token_names TEXT[],
    mentioned_keywords TEXT[],
    like_count BIGINT,
    reply_count BIGINT,
    repost_count BIGINT,
    quote_count BIGINT,
    view_count BIGINT,
    is_original_post BOOLEAN,
    is_reply BOOLEAN,
    is_quote BOOLEAN,
    raw_json JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS token_kol_links (
    id BIGSERIAL PRIMARY KEY,
    token_id BIGINT NOT NULL REFERENCES tokens(id) ON DELETE CASCADE,
    kol_post_id BIGINT NOT NULL REFERENCES kol_posts(id) ON DELETE CASCADE,
    kol_account_id BIGINT NOT NULL REFERENCES kol_accounts(id) ON DELETE CASCADE,
    match_method TEXT NOT NULL,
    match_confidence NUMERIC NOT NULL,
    matched_text TEXT,
    matched_value TEXT,
    token_time_reference TEXT,
    minutes_from_t0 NUMERIC,
    minutes_from_t2 NUMERIC,
    is_before_smart_wallet_entry BOOLEAN,
    classification TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(token_id, kol_post_id, match_method, matched_value)
);

CREATE TABLE IF NOT EXISTS token_outcomes (
    id BIGSERIAL PRIMARY KEY,
    token_id BIGINT NOT NULL UNIQUE REFERENCES tokens(id) ON DELETE CASCADE,
    base_snapshot_at TIMESTAMPTZ,
    base_price_usd NUMERIC,
    price_24h NUMERIC,
    price_72h NUMERIC,
    roi_24h NUMERIC,
    roi_72h NUMERIC,
    max_roi_24h NUMERIC,
    max_roi_72h NUMERIC,
    winner_24h BOOLEAN,
    winner_72h BOOLEAN,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_token_snapshots_token_time ON token_snapshots(token_id, snapshot_at);
CREATE INDEX IF NOT EXISTS idx_token_traders_token_time ON token_traders(token_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_token_traders_wallet ON token_traders(wallet_address);
CREATE INDEX IF NOT EXISTS idx_kol_posts_posted_at ON kol_posts(posted_at);
CREATE INDEX IF NOT EXISTS idx_token_kol_links_token ON token_kol_links(token_id);
