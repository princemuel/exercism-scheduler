CREATE TABLE track_stats (
    title TEXT PRIMARY KEY,
    category TEXT,
    total INTEGER,
    completed INTEGER DEFAULT 0
);
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
