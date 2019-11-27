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



INSERT INTO tracks(track_uuid,track_title, album_title, artist, length, track_url,album_art_url) VALUES('275fc399a955403dacb158cdb6f273b5','Stronger','Graduation', 'Kanye West', '000511','http://localhost:8000/media/Waka_waka.mp3','https://i.ytimg.com/vi/pRpeEdMmmQ0/maxresdefault.jpg');
/*

uuid: 275fc399-a955-403d-acb1-58cdb6f273b5
*/
