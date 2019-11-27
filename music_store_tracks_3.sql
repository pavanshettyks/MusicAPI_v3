-- $ sqlite3 music_store.db < sqlite.sql


PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS tracks;

CREATE TABLE tracks (
	track_title VARCHAR,
	album_title VARCHAR,
	artist VARCHAR,
	length TIME,
	track_url VARCHAR,
	album_art_url VARCHAR,
	track_uuid GUID primary key
);

INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url) VALUES('32de3075797a435694379909451645a5','I Gotta Feeling','The E.N.D.', 'The Black Eyed Peas', '000448','http://localhost:8000/media/waving_flag.mp3','http://images.genius.com/2d335571e608b43f30bd8a89e1fa6d38.1000x1000x1.jpg');

/*
uuid: 32de3075-797a-4356-9437-9909451645a5
*/
