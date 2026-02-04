-- Таблица пользователей (основная)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения подарков (привязана к пользователю по telegram_id)
CREATE TABLE IF NOT EXISTS gift (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    gift_name VARCHAR(150) NOT NULL,
    comment VARCHAR(255),
    names VARCHAR(50) NOT NULL,
    is_gift BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения записей о расходах (упрощенная)
CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    total_sum NUMERIC(10, 2) NOT NULL,
    category_name VARCHAR(100) NOT NULL, -- Название категории напрямую
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comments VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения ДОХОДОВ
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    source VARCHAR(100), -- источник дохода (зарплата, фриланс и т.д.)
    record_date DATE DEFAULT CURRENT_DATE,
    comments VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица для хранения итогов по месяцам
CREATE TABLE IF NOT EXISTS monthly_summary (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
    month_year DATE NOT NULL, -- Первый день месяца
    total_income NUMERIC(10, 2) DEFAULT 0.00,
    total_expense NUMERIC(10, 2) DEFAULT 0.00,
    net_balance NUMERIC(10, 2) DEFAULT 0.00,
    UNIQUE(telegram_id, month_year)
);