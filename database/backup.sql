PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE track_stats (
    title TEXT PRIMARY KEY,
    category TEXT,
    total INTEGER,
    completed INTEGER DEFAULT 0
);
INSERT INTO track_stats VALUES('sqlite','database',28,7);
INSERT INTO track_stats VALUES('python','scripting',140,29);
INSERT INTO track_stats VALUES('jq','shell',74,3);
INSERT INTO track_stats VALUES('rust','system',99,27);
INSERT INTO track_stats VALUES('javascript','scripting',150,31);
INSERT INTO track_stats VALUES('typescript','scripting',100,25);
INSERT INTO track_stats VALUES('go','scripting',141,9);
INSERT INTO track_stats VALUES('c','system',82,3);
INSERT INTO track_stats VALUES('cpp','system',99,5);
INSERT INTO track_stats VALUES('bash','shell',92,9);
INSERT INTO track_stats VALUES('awk','shell',83,3);
INSERT INTO track_stats VALUES('julia','functional',101,4);
CREATE TABLE daily_schedule (
    date TEXT PRIMARY KEY,
    main_tracks TEXT CHECK(json_valid(main_tracks)),
    optional_tracks TEXT CHECK(json_valid(optional_tracks))
);
CREATE TABLE progress_log (
    date TEXT,
    track TEXT,
    completed INTEGER,
    carried_over INTEGER DEFAULT 0,
    PRIMARY KEY (date, track),
    FOREIGN KEY (date) REFERENCES daily_schedule(date) ON DELETE CASCADE,
    FOREIGN KEY (track) REFERENCES track_stats(title) ON DELETE CASCADE
);
CREATE INDEX idx_progress_log_date ON progress_log(date);
CREATE INDEX idx_progress_log_track ON progress_log(track);
COMMIT;
