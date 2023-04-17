DROP TABLE IF EXISTS `prompts`;

CREATE TABLE prompts (
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    command VARCHAR(255),
    voice_id VARCHAR(255) REFERENCES voices(voice_id),
    user_id BIGINT REFERENCES users(user_id),
    server_id BIGINT NOT NULL,
    prompt TEXT,
    response TEXT,
    num_chars INT,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    path VARCHAR(255)
);

DROP TABLE IF EXISTS `users`;

CREATE TABLE users (
    user_id BIGINT NOT NULL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    privileges VARCHAR(255) DEFAULT 'normal_user',
    total_chars_used INT DEFAULT 0,
    monthly_char_limit INT DEFAULT 6000,
    monthly_chars_used INT DEFAULT 0,
    char_credit INT DEFAULT 0,
    last_char_reset TIMESTAMP DEFAULT '1970-01-01 00:00:01',
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS `voices`;

CREATE TABLE voices (
    voice_id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255),
    accent VARCHAR(255),
    user_id BIGINT REFERENCES users(user_id),
    server_id BIGINT,
    server_name VARCHAR(255),
    path VARCHAR(255) NOT NULL,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS `transactions`;

CREATE TABLE transactions(
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id), 
    payment_method VARCHAR(255) NOT NULL,
    chars_purchased INT NOT NULL,
    amount_cad DECIMAL NOT NULL,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);