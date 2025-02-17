-- Таблица для хранения подарков
CREATE TABLE IF NOT EXISTS gift (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    gift_name VARCHAR(150) NOT NULL,
    comment VARCHAR(255),
    names VARCHAR(50) NOT NULL,
    is_gift BOOLEAN DEFAULT FALSE
);

-- Таблица для хранения ролей с доступом (в доработке)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    role VARCHAR(20) DEFAULT 'user'
);

-- Таблица для хранения категорий расходов
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE -- Название категории
);

-- Таблица для хранения записей о расходах
CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    total_sum NUMERIC(10, 2) NOT NULL, -- Потраченная сумма
    category_id INT REFERENCES categories(id) ON DELETE CASCADE, -- Внешний ключ на категорию
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата траты
    comments VARCHAR(255) -- Комментарий
);

-- Таблица для хранения итогов по месяцам
CREATE TABLE IF NOT EXISTS monthly_summary (
    id SERIAL PRIMARY KEY,
    month_year DATE NOT NULL, -- Месяц и год (например, '2023-03-01' для марта 2023)
    total_income NUMERIC(10, 2) DEFAULT 0.00, -- Общая сумма доходов
    total_expense NUMERIC(10, 2) DEFAULT 0.00, -- Общая сумма расходов
    net_balance NUMERIC(10, 2) DEFAULT 0.00 -- Чистый баланс (доходы - расходы)
);