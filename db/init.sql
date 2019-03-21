CREATE DATABASE 1x2_betandwin;
use 1x2_betandwin;

CREATE TABLE matches (
  match_id VARCHAR(20) PRIMARY KEY,
  home_team VARCHAR(20),
  away_team VARCHAR(20),
  home_victory FLOAT(20),
  draw FLOAT(20),
  away_victory FLOAT(20),
  under_2_goals FLOAT(20),
  2_3_goals FLOAT(20),
  over_3_goals FLOAT(20)
);

CREATE TABLE bets (
  match_id VARCHAR(20),
  bet_type VARCHAR(500),
  number_of_bets INTEGER(20),
  FOREIGN KEY(match_id) REFERENCES matches(match_id)
);

CREATE TABLE results (
  match_id VARCHAR(20),
  result VARCHAR(20),
  goals_result VARCHAR(20)
);

CREATE TABLE tickets (
  ticket_id varchar(20),
  bets varchar(1000)
);

DELIMITER $$
CREATE TRIGGER match_ended AFTER INSERT ON results
FOR EACH ROW
BEGIN
    DELETE FROM bets WHERE (match_id = NEW.match_id);
    DELETE FROM matches WHERE (match_id = NEW.match_id);
END$$
DELIMITER ;