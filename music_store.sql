-- $ sqlite3 music_store.db < sqlite.sql


PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS playlist;
DROP TABLE IF EXISTS playlist_tracks;
DROP TABLE IF EXISTS description;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS tracks;



CREATE TABLE user (
	username VARCHAR primary key,
	hashed_password VARCHAR,
	display_name VARCHAR,
	homepage_url VARCHAR,
	email VARCHAR
);

INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_anthony','Anthony','pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3' ,'test.com', 'anthony@csu.fullerton.edu');
INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_pavan','Pavan', 'pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3','est.com','pavan@csu.fullerton.edu');
INSERT INTO user(username, display_name, hashed_password, homepage_url, email) VALUES('user_priyanka','Priyanka','pbkdf2:sha256:150000$bGSxegkS$7598256a7ff683743b0dbe182ee77eec4afce1c8339914f482e4e626491b28b3', 'ests.com','priyanka@csu.fullerton.edu');


CREATE TABLE tracks (
	track_title VARCHAR,
	album_title VARCHAR,
	artist VARCHAR,
	length TIME,
	track_url VARCHAR primary key,
	album_art_url VARCHAR
);

INSERT INTO tracks(track_title, album_title, artist, length, track_url,album_art_url) VALUES('Stronger','Graduation', 'Kanye West', '000511','Waka_waka.mp3','https://i.ytimg.com/vi/pRpeEdMmmQ0/maxresdefault.jpg');
INSERT INTO tracks(track_title, album_title, artist, length, track_url,album_art_url) VALUES('Yeah!','Confessions', 'Usher', '000410','tokyo_drift.mp3','https://images-na.ssl-images-amazon.com/images/I/81cw8NVT36L._SX342_.jpg');
INSERT INTO tracks(track_title, album_title, artist, length, track_url,album_art_url) VALUES('I Gotta Feeling','The E.N.D.', 'The Black Eyed Peas', '000448','waving_flag.mp3','http://images.genius.com/2d335571e608b43f30bd8a89e1fa6d38.1000x1000x1.jpg');



CREATE TABLE description (
  description_id INTEGER primary key,
  description VARCHAR,
  username VARCHAR,
  track_url VARCHAR,
  FOREIGN KEY (username) REFERENCES user(username) ON DELETE CASCADE,
	FOREIGN KEY (track_url) REFERENCES tracks(track_url) ON DELETE CASCADE

);

INSERT INTO description(username, track_url, description) VALUES('user_pavan','Waka_waka.mp3', 'workout song by kanye west');
INSERT INTO description(username, track_url, description) VALUES('user_pavan','tokyo_drift.mp3', 'favorite usher song');
INSERT INTO description(username, track_url, description) VALUES('user_priyanka','tokyo_drift.mp3', 'favorite usher song');
INSERT INTO description(username, track_url, description) VALUES('user_anthony','waving_flag.mp3', 'classic black eyed peas song');

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
	track_url VARCHAR,
	FOREIGN KEY (username) REFERENCES user(username) ON DELETE CASCADE,
	FOREIGN KEY (track_url) REFERENCES tracks(track_url) ON DELETE CASCADE
);

INSERT INTO playlist_tracks(username, playlist_title, track_url) VALUES('user_priyanka','All', 'Waka_waka.mp3');
INSERT INTO playlist_tracks(username, playlist_title, track_url) VALUES('user_priyanka','All', 'tokyo_drift.mp3');
INSERT INTO playlist_tracks(username, playlist_title, track_url) VALUES('user_priyanka','All', 'waving_flag.mp3');
INSERT INTO playlist_tracks(username, playlist_title, track_url) VALUES('user_anthony','Some', 'Waka_waka.mp3');
INSERT INTO playlist_tracks(username, playlist_title, track_url) VALUES('user_anthony','Some', 'tokyo_drift.mp3');
