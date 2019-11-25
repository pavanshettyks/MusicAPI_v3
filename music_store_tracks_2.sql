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


/*
uuid: ac3d3e62-d611-4013-8bc9-22d90623d5db
*/