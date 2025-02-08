CREATE TABLE IF NOT EXISTS gift (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    gift_name VARCHAR(150) NOT NULL,
    comment VARCHAR(255),
    names VARCHAR(50) NOT NULL,
    is_gift BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    total_sum NUMERIC(10, 2),
    direction VARCHAR(255),
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    person_name VARCHAR(255)
);