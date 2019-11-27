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


INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url) VALUES('ac3d3e62d61140138bc922d90623d5db','Yeah!','Confessions', 'Usher', '000410','http://localhost:8000/media/tokyo_drift.mp3','https://images-na.ssl-images-amazon.com/images/I/81cw8NVT36L._SX342_.jpg');

/*
uuid: ac3d3e62-d611-4013-8bc9-22d90623d5db
*/
