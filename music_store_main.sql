-- $ sqlite3 music_store.db < sqlite.sql


PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS playlist;
DROP TABLE IF EXISTS playlist_tracks;
DROP TABLE IF EXISTS description;
DROP TABLE IF EXISTS user;

CREATE TABLE user (
	username VARCHAR primary key,
	hashed_password VARCHAR,
	display_name VARCHAR,
	homepage_url VARCHAR,
	email VARCHAR
);

INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_anthony','Anthony','pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3' ,'/user?username=user_anthony', 'anthony@csu.fullerton.edu');
INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_pavan','Pavan', 'pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3','/user?username=user_pavan','pavan@csu.fullerton.edu');
INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_priyanka','Priyanka','pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3', '/user?username=user_priyanka','priyanka@csu.fullerton.edu');



CREATE TABLE description (
  description_id INTEGER primary key,
  description VARCHAR,
  username VARCHAR,
  track_uuid GUID,
  FOREIGN KEY (username) REFERENCES user(username) ON DELETE CASCADE
/*	FOREIGN KEY (track_url) REFERENCES tracks(track_url) ON DELETE CASCADE */

);

INSERT INTO description(username, track_uuid, description) VALUES('user_pavan','275fc399-a955-403d-acb1-58cdb6f273b5', 'workout song by kanye west');
INSERT INTO description(username, track_uuid, description) VALUES('user_pavan','ac3d3e62-d611-4013-8bc9-22d90623d5db', 'favorite usher song');
INSERT INTO description(username, track_uuid, description) VALUES('user_priyanka','ac3d3e62-d611-4013-8bc9-22d90623d5db', 'favorite usher song');
INSERT INTO description(username, track_uuid, description) VALUES('user_anthony','32de3075-797a-4356-9437-9909451645a5', 'classic black eyed peas song');

CREATE TABLE playlist (
	playlist_id INTEGER primary key,
	playlist_title VARCHAR,
	username VARCHAR,
	description VARCHAR,
	FOREIGN KEY (username) REFERENCES user(username)
);

INSERT INTO playlist(playlist_title, username, description) VALUES('All','user_priyanka', 'This playlist contains all of my songs');
INSERT INTO playlist(playlist_title, username, description) VALUES('Some','user_anthony', 'This playlist contains some of my songs');

CREATE TABLE playlist_tracks (
	playlist_id INTEGER primary key,
	username VARCHAR,
	playlist_title VARCHAR,
	track_uuid GUID,
	FOREIGN KEY (username) REFERENCES user(username) ON DELETE CASCADE
/*	FOREIGN KEY (track_url) REFERENCES tracks(track_url) ON DELETE CASCADE */
);

INSERT INTO playlist_tracks(username, playlist_title, track_uuid) VALUES('user_priyanka','All', '275fc399-a955-403d-acb1-58cdb6f273b5');
INSERT INTO playlist_tracks(username, playlist_title, track_uuid) VALUES('user_priyanka','All', 'ac3d3e62-d611-4013-8bc9-22d90623d5db');
INSERT INTO playlist_tracks(username, playlist_title, track_uuid) VALUES('user_priyanka','All', '32de3075-797a-4356-9437-9909451645a5');
INSERT INTO playlist_tracks(username, playlist_title, track_uuid) VALUES('user_anthony','Some', '275fc399-a955-403d-acb1-58cdb6f273b5');
INSERT INTO playlist_tracks(username, playlist_title, track_uuid) VALUES('user_anthony','Some', 'ac3d3e62-d611-4013-8bc9-22d90623d5db');