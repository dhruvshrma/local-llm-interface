CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  model TEXT,
  start_time TEXT
);

CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  conversation_id TEXT REFERENCES conversations(id),
  role TEXT,
  content TEXT,
  timestamp_utc TEXT
);

CREATE VIRTUAL TABLE messages_fts USING FTS5 (
  content,
  content=messages,
  content_rowid=id
);
