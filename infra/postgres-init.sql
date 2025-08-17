-- Enable extensions if needed, e.g., for vector embeddings
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Main entity tables
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    base_price NUMERIC(10, 2) NOT NULL,
    cost NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE competitors (
    competitor_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    website_url VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Time-series data tables
CREATE TABLE competitor_prices (
    price_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    competitor_id INTEGER NOT NULL REFERENCES competitors(competitor_id),
    price NUMERIC(10, 2) NOT NULL,
    in_stock BOOLEAN DEFAULT TRUE,
    observed_at TIMESTAMPTZ NOT NULL,
    UNIQUE(product_id, competitor_id, observed_at)
);

CREATE TABLE reviews (
    review_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    source VARCHAR(50), -- e.g., 'amazon', 'internal_site'
    review_text TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    sentiment_label VARCHAR(20), -- e.g., 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    sentiment_score FLOAT,
    reviewed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE product_daily_kpi (
    kpi_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    kpi_date DATE NOT NULL,
    revenue NUMERIC(12, 2),
    orders INTEGER,
    conversion_rate FLOAT,
    average_price NUMERIC(10, 2),
    UNIQUE(product_id, kpi_date)
);

-- RL/ML model related tables
CREATE TABLE rl_policies (
    policy_id SERIAL PRIMARY KEY,
    policy_name VARCHAR(100) NOT NULL UNIQUE,
    algorithm VARCHAR(50), -- e.g., 'PPO', 'SAC'
    hyperparameters JSONB,
    storage_path VARCHAR(255) NOT NULL, -- e.g., s3://bucket/path/to/model.zip
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE price_recommendations (
    recommendation_id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    policy_id INTEGER REFERENCES rl_policies(policy_id),
    recommended_price NUMERIC(10, 2) NOT NULL,
    request_constraints JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Feature store for the RL model
CREATE MATERIALIZED VIEW fv_product_context AS
SELECT
    p.product_id,
    p.base_price,
    p.cost,
    -- Latest competitor prices
    (SELECT AVG(cp.price) FROM competitor_prices cp WHERE cp.product_id = p.product_id AND cp.observed_at > NOW() - INTERVAL '7 days') as avg_competitor_price_7d,
    -- Latest sentiment
    (SELECT AVG(r.sentiment_score) FROM reviews r WHERE r.product_id = p.product_id AND r.reviewed_at > NOW() - INTERVAL '30 days') as avg_sentiment_30d,
    -- Recent demand signals
    (SELECT AVG(kpi.orders) FROM product_daily_kpi kpi WHERE kpi.product_id = p.product_id AND kpi.kpi_date > NOW() - INTERVAL '14 days') as avg_orders_14d
FROM products p;

-- A unique index is required for concurrent refreshing
CREATE UNIQUE INDEX uix_fv_product_context_product_id ON fv_product_context (product_id);

-- Indexes for performance
CREATE INDEX idx_competitor_prices_product_time ON competitor_prices(product_id, observed_at DESC);
CREATE INDEX idx_reviews_product_time ON reviews(product_id, reviewed_at DESC);
CREATE INDEX idx_product_daily_kpi_product_date ON product_daily_kpi(product_id, kpi_date DESC);

-- Trigger to auto-update 'updated_at' timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON products
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();
