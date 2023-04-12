DROP TABLE IF EXISTS `prompts`;

CREATE TABLE prompts (
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    command VARCHAR(255),
    user_id BIGINT REFERENCES users(user_id),
    username VARCHAR(255),
    prompt TEXT,
    response TEXT,
    num_chars INT,
    path VARCHAR(255)
);

DROP TABLE IF EXISTS `users`;

CREATE TABLE users (
    user_id BIGINT NOT NULL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    monthly_char_limit INT DEFAULT 6000,
    monthly_chars_used INT DEFAULT 0,
    last_char_reset TIMESTAMP DEFAULT '1970-01-01 00:00:01',
    total_chars_used INT DEFAULT 0,
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS `voices`;

CREATE TABLE voices (
    voice_id VARCHAR(255) NOT NULL PRIMARY KEY,
    name VARCHAR(255),
    is_private BOOLEAN DEFAULT TRUE,
    user_id BIGINT REFERENCES users(user_id),
    date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    path VARCHAR(255) NOT NULL
);