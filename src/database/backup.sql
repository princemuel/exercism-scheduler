PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

CREATE TABLE tracks (
    title TEXT PRIMARY KEY,
    category TEXT,
    total INTEGER,
    completed INTEGER DEFAULT 0
);

INSERT INTO tracks
VALUES('sqlite', 'database', 28, 7);

INSERT INTO tracks
VALUES('python', 'scripting', 140, 29);

INSERT INTO tracks
VALUES('jq', 'shell', 74, 3);

INSERT INTO tracks
VALUES('rust', 'system', 99, 27);

INSERT INTO tracks
VALUES('javascript', 'scripting', 150, 31);

INSERT INTO tracks
VALUES('typescript', 'scripting', 100, 25);

INSERT INTO tracks
VALUES('go', 'scripting', 141, 9);

INSERT INTO tracks
VALUES('c', 'system', 82, 3);

INSERT INTO tracks
VALUES('cpp', 'system', 99, 5);

INSERT INTO tracks
VALUES('bash', 'shell', 92, 9);

INSERT INTO tracks
VALUES('awk', 'shell', 83, 3);

INSERT INTO tracks
VALUES('julia', 'functional', 101, 4);

CREATE TABLE schedule (
    date TEXT PRIMARY KEY,
    core TEXT CHECK(json_valid(core)),
    extra TEXT CHECK(json_valid(extra))
);

CREATE TABLE logs (
    date TEXT,
    track TEXT,
    completed INTEGER,
    pending INTEGER DEFAULT 0,
    PRIMARY KEY (date, track),
    FOREIGN KEY (date) REFERENCES schedule(date) ON DELETE CASCADE,
    FOREIGN KEY (track) REFERENCES tracks(title) ON DELETE CASCADE
);

CREATE INDEX idx_logs_date ON logs(date);

CREATE INDEX idx_logs_track ON logs(track);

COMMIT;
