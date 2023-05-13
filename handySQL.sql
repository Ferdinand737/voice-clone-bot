select * from prompts order by date_time desc;
ALTER TABLE users ADD COLUMN char_credit INT DEFAULT 0;
update users set privileges='admin' WHERE user_id=273300302541881344