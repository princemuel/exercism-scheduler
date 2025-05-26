CREATE TABLE tracks (
    title TEXT PRIMARY KEY,
    category TEXT,
    total INTEGER,
    completed INTEGER DEFAULT 0
);

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
