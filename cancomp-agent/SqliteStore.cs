using Microsoft.Data.Sqlite;

namespace BmCancomp;

public sealed class SqliteStore : IDisposable
{
    readonly string _path;
    readonly SqliteConnection _cx;

    public SqliteStore(string dataDir)
    {
        Directory.CreateDirectory(dataDir);
        _path = Path.Combine(dataDir, "cancomp.db");
        _cx = new SqliteConnection($"Data Source={_path}");
        _cx.Open();
    }

    public string PathName => _path;

    public void Init()
    {
        using var cmd = _cx.CreateCommand();
        cmd.CommandText = """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS events (
              id TEXT PRIMARY KEY,
              source TEXT NOT NULL,
              kg REAL,
              starch_pct REAL,
              ts TEXT NOT NULL,
              raw TEXT NOT NULL,
              sync TEXT NOT NULL DEFAULT 'queued',
              last_error TEXT,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS raw_log (
              ts TEXT NOT NULL,
              port TEXT NOT NULL,
              raw TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_events_sync ON events(sync, created_at);
            """;
        cmd.ExecuteNonQuery();
    }

    public void LogRaw(string port, string raw)
    {
        using var cmd = _cx.CreateCommand();
        cmd.CommandText = "INSERT INTO raw_log(ts,port,raw) VALUES($ts,$p,$r)";
        cmd.Parameters.AddWithValue("$ts", DateTimeOffset.Now.ToString("o"));
        cmd.Parameters.AddWithValue("$p", port);
        cmd.Parameters.AddWithValue("$r", raw.Length > 200 ? raw[..200] : raw);
        cmd.ExecuteNonQuery();
        using var trim = _cx.CreateCommand();
        trim.CommandText = "DELETE FROM raw_log WHERE ts < $cut";
        trim.Parameters.AddWithValue("$cut", DateTimeOffset.Now.AddDays(-2).ToString("o"));
        trim.ExecuteNonQuery();
    }

    public void InsertAccepted(IngestPayload p)
    {
        using var cmd = _cx.CreateCommand();
        cmd.CommandText = """
            INSERT OR IGNORE INTO events(id,source,kg,starch_pct,ts,raw,sync,created_at)
            VALUES($id,$src,$kg,$st,$ts,$raw,'queued',$now)
            """;
        cmd.Parameters.AddWithValue("$id", p.Id);
        cmd.Parameters.AddWithValue("$src", p.Source);
        cmd.Parameters.AddWithValue("$kg", (object?)p.Kg ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$st", (object?)p.StarchPct ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$ts", p.Ts);
        cmd.Parameters.AddWithValue("$raw", p.Raw);
        cmd.Parameters.AddWithValue("$now", DateTimeOffset.Now.ToString("o"));
        cmd.ExecuteNonQuery();
    }

    public List<IngestPayload> Dequeue(int n = 20)
    {
        using var cmd = _cx.CreateCommand();
        cmd.CommandText = "SELECT id,source,kg,starch_pct,ts,raw FROM events WHERE sync IN ('queued','retry') ORDER BY created_at LIMIT $n";
        cmd.Parameters.AddWithValue("$n", n);
        var list = new List<IngestPayload>();
        using var rd = cmd.ExecuteReader();
        while (rd.Read())
        {
            list.Add(new IngestPayload
            {
                Id = rd.GetString(0),
                Source = rd.GetString(1),
                Kg = rd.IsDBNull(2) ? null : rd.GetDouble(2),
                StarchPct = rd.IsDBNull(3) ? null : rd.GetDouble(3),
                Ts = rd.GetString(4),
                Raw = rd.GetString(5),
            });
        }
        return list;
    }

    public void Mark(string id, string sync, string? err = null)
    {
        using var cmd = _cx.CreateCommand();
        cmd.CommandText = "UPDATE events SET sync=$s, last_error=$e WHERE id=$id";
        cmd.Parameters.AddWithValue("$s", sync);
        cmd.Parameters.AddWithValue("$e", (object?)err ?? DBNull.Value);
        cmd.Parameters.AddWithValue("$id", id);
        cmd.ExecuteNonQuery();
    }

    public (int queued, int sent, int fail) Counts()
    {
        int Q(string s)
        {
            using var cmd = _cx.CreateCommand();
            cmd.CommandText = "SELECT COUNT(*) FROM events WHERE sync=$s";
            cmd.Parameters.AddWithValue("$s", s);
            return Convert.ToInt32(cmd.ExecuteScalar());
        }
        return (Q("queued") + Q("retry"), Q("sent"), Q("fail"));
    }

    public List<StoredEvent> Recent(int n = 40)
    {
        using var cmd = _cx.CreateCommand();
        cmd.CommandText = "SELECT rowid,id,source,kg,starch_pct,ts,raw,sync FROM events ORDER BY created_at DESC LIMIT $n";
        cmd.Parameters.AddWithValue("$n", n);
        var list = new List<StoredEvent>();
        using var rd = cmd.ExecuteReader();
        while (rd.Read())
        {
            list.Add(new StoredEvent
            {
                RowId = rd.GetInt64(0),
                Id = rd.GetString(1),
                Source = rd.GetString(2),
                Kg = rd.IsDBNull(3) ? null : rd.GetDouble(3),
                StarchPct = rd.IsDBNull(4) ? null : rd.GetDouble(4),
                Ts = rd.GetString(5),
                Raw = rd.GetString(6),
                Sync = rd.GetString(7),
            });
        }
        return list;
    }

    public void Dispose() => _cx.Dispose();
}
