using System.IO.Ports;

namespace BmCancomp;

public sealed class MainForm : Form
{
    readonly AppConfig _cfg;
    readonly SqliteStore _store;
    readonly IngestClient _sync = new();
    readonly System.Windows.Forms.Timer _tick = new() { Interval = 2500 };
    ListenPort? _scalePort;
    ListenPort? _starchPort;
    PlateauFilter _kgFilter;
    PlateauFilter _stFilter;
    readonly Label _kgLive = BigNum("— kg");
    readonly Label _stLive = BigNum("— %");
    readonly Label _kgHold = BigNum("—");
    readonly Label _stHold = BigNum("—");
    readonly Label _scaleSt = Status("cân: đóng");
    readonly Label _starchSt = Status("bột: đóng");
    readonly Label _syncSt = Status("sync: chờ");
    readonly Label _clock = Status("");
    readonly TextBox _log = new() { Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, Font = new Font("Consolas", 9f), BackColor = Color.FromArgb(26, 8, 12), ForeColor = Color.FromArgb(232, 197, 71), BorderStyle = BorderStyle.None, Dock = DockStyle.Fill };
    readonly DataGridView _grid = new() { Dock = DockStyle.Fill, ReadOnly = true, AllowUserToAddRows = false, AllowUserToDeleteRows = false, RowHeadersVisible = false, AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill, BackgroundColor = Color.FromArgb(42, 16, 22), GridColor = Color.FromArgb(107, 42, 52), BorderStyle = BorderStyle.None };
    bool _running;

    public MainForm(AppConfig cfg, SqliteStore store)
    {
        _cfg = cfg; _store = store; _kgFilter = MakeKg(); _stFilter = MakeSt();
        Text = "BM CANcomp — Bình Minh cầu cân";
        Width = 1180; Height = 760; StartPosition = FormStartPosition.CenterScreen;
        BackColor = Color.FromArgb(42, 10, 18); ForeColor = Color.FromArgb(246, 238, 230);
        Font = new Font("Segoe UI", 10f); MinimumSize = new Size(960, 640);
        var top = new Panel { Dock = DockStyle.Top, Height = 92, Padding = new Padding(16, 12, 16, 8) };
        top.Controls.Add(new Label { AutoSize = true, Text = "BM CANcomp", Font = new Font("Segoe UI Semibold", 22f), ForeColor = Color.FromArgb(212, 175, 55), Location = new Point(16, 10) });
        top.Controls.Add(new Label { AutoSize = true, Text = "Nghe RS232 · lọc cao nguyên 2 s · SQLite · POST /api/ingest", ForeColor = Color.FromArgb(201, 180, 173), Location = new Point(18, 50) });
        _clock.Location = new Point(880, 18); _clock.AutoSize = true; top.Controls.Add(_clock);
        var kpi = new TableLayoutPanel { Dock = DockStyle.Top, Height = 168, ColumnCount = 4, Padding = new Padding(12, 0, 12, 8) };
        for (int i = 0; i < 4; i++) kpi.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 25));
        kpi.Controls.Add(Card("Cân xe · live", _kgLive, _scaleSt), 0, 0);
        kpi.Controls.Add(Card("Cân xe · cao nguyên", _kgHold, Hint("một số / lượt")), 1, 0);
        kpi.Controls.Add(Card("Điểm bột · live", _stLive, _starchSt), 2, 0);
        kpi.Controls.Add(Card("Điểm bột · cao nguyên", _stHold, Hint("idle 000000= bỏ")), 3, 0);
        var bar = new FlowLayoutPanel { Dock = DockStyle.Top, Height = 52, Padding = new Padding(12, 6, 12, 6), WrapContents = false };
        var btnStart = Wine("Bắt đầu nghe"); var btnStop = Ghost("Dừng"); var btnSync = Ghost("Đẩy hàng đợi"); var btnPorts = Ghost("Làm mới COM"); var btnAdmin = Gold("Admin");
        btnStop.Enabled = false;
        bar.Controls.AddRange(new Control[] { btnStart, btnStop, btnSync, btnPorts, btnAdmin, _syncSt });
        var split = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical, SplitterDistance = 520, BackColor = Color.FromArgb(60, 20, 28) };
        var left = new Panel { Dock = DockStyle.Fill, Padding = new Padding(12, 4, 6, 12) };
        var right = new Panel { Dock = DockStyle.Fill, Padding = new Padding(6, 4, 12, 12) };
        left.Controls.Add(Box("Phiếu đã lấy (ổn định)", _grid));
        right.Controls.Add(Box("Raw RS232", _log));
        split.Panel1.Controls.Add(left); split.Panel2.Controls.Add(right);
        Controls.Add(split); Controls.Add(bar); Controls.Add(kpi); Controls.Add(top);
        StyleGrid(); ReloadGrid();
        btnStart.Click += (_, _) => { Start(); btnStart.Enabled = false; btnStop.Enabled = true; };
        btnStop.Click += (_, _) => { Stop(); btnStart.Enabled = true; btnStop.Enabled = false; };
        btnSync.Click += async (_, _) => await FlushAsync();
        btnPorts.Click += (_, _) => Log("COM: " + string.Join(", ", SerialPort.GetPortNames()));
        btnAdmin.Click += (_, _) => OpenAdmin();
        FormClosing += (_, e) => Stop();
        _tick.Tick += async (_, _) => {
            _clock.Text = DateTime.Now.ToString("HH:mm:ss  dd/MM/yyyy");
            if (_running) await FlushAsync();
            var c = _store.Counts();
            _syncSt.Text = $"hàng đợi {c.queued} · đã gửi {c.sent} · lỗi {c.fail}";
        };
        _tick.Start();
        Log($"DB {_store.PathName}");
        Log($"Cấu hình {AppConfig.ConfigPath}");
        Log("COM: " + string.Join(", ", SerialPort.GetPortNames()));
        Log("Máy bột 1200 8N1, DTR/RTS tắt. Không ghi lên đầu cân.");
    }

    PlateauFilter MakeKg() => new(_cfg.Scale.FloorKg, _cfg.Scale.MinPeakKg, _cfg.Scale.BandKg, _cfg.Scale.WindowSec, _cfg.Scale.MaxKg);
    PlateauFilter MakeSt() => new(_cfg.Starch.FloorPct, _cfg.Starch.MinPeakPct, _cfg.Starch.BandPct, _cfg.Starch.WindowSec, _cfg.Starch.MaxPct);

    void Start()
    {
        Stop(); _kgFilter = MakeKg(); _stFilter = MakeSt();
        try { _scalePort = new ListenPort(_cfg.Scale); _scalePort.Status += (_, s) => BeginInvoke(() => { _scaleSt.Text = s; Log("[cân] " + s); }); _scalePort.Frame += (_, e) => BeginInvoke(() => OnScale(e)); _scalePort.Open(); }
        catch (Exception ex) { Log("[cân] " + ex.Message); }
        try { _starchPort = new ListenPort(_cfg.Starch); _starchPort.Status += (_, s) => BeginInvoke(() => { _starchSt.Text = s; Log("[bột] " + s); }); _starchPort.Frame += (_, e) => BeginInvoke(() => OnStarch(e)); _starchPort.Open(); }
        catch (Exception ex) { Log("[bột] " + ex.Message); }
        _running = true; Log("Đang nghe (listen-only).");
    }
    void Stop() { _running = false; _scalePort?.Dispose(); _starchPort?.Dispose(); _scalePort = null; _starchPort = null; }

    void OnScale(FrameEventArgs e)
    {
        _store.LogRaw(e.Port, e.Raw); Log($"C {e.Raw}");
        if (!KingbirdParser.TryParse(e.Raw, out var kg, out _)) return;
        _kgLive.Text = kg.ToString("N0") + " kg";
        if (_kgFilter.OnSample(e.Ts, kg, out var plateau))
        {
            var p = new IngestPayload { Source = "kingbird", Kg = Math.Round(plateau, 0), Stable = true, Ts = DateTimeOffset.Now.ToString("o"), Raw = e.Raw };
            _store.InsertAccepted(p); _kgHold.Text = p.Kg!.Value.ToString("N0") + " kg"; Log($"* CAO NGUYEN can {p.Kg:N0} kg"); ReloadGrid();
        }
    }
    void OnStarch(FrameEventArgs e)
    {
        _store.LogRaw(e.Port, e.Raw); Log($"B {e.Raw}");
        if (!StarchParser.TryParse(e.Raw, out var pct)) return;
        _stLive.Text = pct.ToString("0.00") + " %";
        if (_stFilter.OnSample(e.Ts, pct, out var plateau))
        {
            var p = new IngestPayload { Source = "starch", StarchPct = Math.Round(plateau, 2), Stable = true, Ts = DateTimeOffset.Now.ToString("o"), Raw = e.Raw };
            _store.InsertAccepted(p); _stHold.Text = p.StarchPct!.Value.ToString("0.00") + " %"; Log($"* CAO NGUYEN bot {p.StarchPct:0.00} %"); ReloadGrid();
        }
    }
    async Task FlushAsync()
    {
        var batch = _store.Dequeue(15);
        foreach (var p in batch)
        {
            p.StationId = _cfg.StationId;
            var (ok, msg) = await _sync.SendAsync(_cfg, p, CancellationToken.None);
            _store.Mark(p.Id, ok ? "sent" : "retry", ok ? null : msg);
            if (!ok) Log("sync " + msg);
        }
        if (batch.Count > 0) ReloadGrid();
    }
    void OpenAdmin()
    {
        using var pin = new Form { Text = "Admin", Width = 340, Height = 160, StartPosition = FormStartPosition.CenterParent, FormBorderStyle = FormBorderStyle.FixedDialog, MaximizeBox = false, MinimizeBox = false, BackColor = Color.FromArgb(42, 10, 18), ForeColor = Color.White };
        var tb = new TextBox { UseSystemPasswordChar = true, Width = 200, Location = new Point(60, 24) };
        var ok = Gold("Vào cài đặt"); ok.Location = new Point(90, 64);
        pin.Controls.Add(new Label { Text = "Mã PIN admin", AutoSize = true, Location = new Point(60, 6) });
        pin.Controls.Add(tb); pin.Controls.Add(ok);
        ok.Click += (_, _) => { if (tb.Text.Trim() != _cfg.AdminPin) { MessageBox.Show("Sai PIN."); return; } pin.DialogResult = DialogResult.OK; };
        if (pin.ShowDialog(this) != DialogResult.OK) return;
        using var s = new SettingsForm(_cfg);
        if (s.ShowDialog(this) == DialogResult.OK) { _cfg.Save(); _kgFilter = MakeKg(); _stFilter = MakeSt(); Log("Đã lưu. Dừng rồi nghe lại nếu đổi COM."); }
    }
    void ReloadGrid()
    {
        _grid.DataSource = _store.Recent(50).Select(x => new { x.Ts, x.Source, Kg = x.Kg, Bot = x.StarchPct, x.Sync, x.Raw }).ToList();
    }
    void Log(string s)
    {
        _log.AppendText(DateTime.Now.ToString("HH:mm:ss") + "  " + s + Environment.NewLine);
        if (_log.TextLength > 80000) _log.Text = _log.Text[^40000..];
    }
    static Label BigNum(string t) => new() { Text = t, Dock = DockStyle.Fill, Font = new Font("Segoe UI", 26f, FontStyle.Bold), ForeColor = Color.FromArgb(232, 197, 71), TextAlign = ContentAlignment.MiddleLeft };
    static Label Status(string t) => new() { Text = t, AutoSize = true, ForeColor = Color.FromArgb(201, 180, 173), Margin = new Padding(12, 14, 8, 0) };
    static Label Hint(string t) => new() { Text = t, Dock = DockStyle.Bottom, Height = 22, ForeColor = Color.FromArgb(201, 180, 173) };
    static Panel Card(string title, Control body, Control foot)
    {
        var p = new Panel { Dock = DockStyle.Fill, Margin = new Padding(6), BackColor = Color.FromArgb(60, 16, 24), Padding = new Padding(12) };
        p.Controls.Add(body); p.Controls.Add(foot);
        p.Controls.Add(new Label { Text = title.ToUpperInvariant(), Dock = DockStyle.Top, Height = 22, Font = new Font("Segoe UI", 8.5f, FontStyle.Bold), ForeColor = Color.FromArgb(212, 175, 55) });
        return p;
    }
    static Panel Box(string title, Control inner)
    {
        var p = new Panel { Dock = DockStyle.Fill, BackColor = Color.FromArgb(60, 16, 24), Padding = new Padding(10) };
        p.Controls.Add(inner);
        p.Controls.Add(new Label { Text = title.ToUpperInvariant(), Dock = DockStyle.Top, Height = 24, Font = new Font("Segoe UI", 8.5f, FontStyle.Bold), ForeColor = Color.FromArgb(212, 175, 55) });
        return p;
    }
    static Button Wine(string t) => Btn(t, Color.FromArgb(180, 35, 51), Color.White);
    static Button Gold(string t) => Btn(t, Color.FromArgb(212, 175, 55), Color.FromArgb(42, 10, 18));
    static Button Ghost(string t) => Btn(t, Color.FromArgb(74, 24, 32), Color.FromArgb(246, 238, 230));
    static Button Btn(string t, Color bg, Color fg) => new() { Text = t, AutoSize = true, Padding = new Padding(12, 4, 12, 4), BackColor = bg, ForeColor = fg, FlatStyle = FlatStyle.Flat, FlatAppearance = { BorderSize = 0 }, Margin = new Padding(4) };
    void StyleGrid()
    {
        _grid.EnableHeadersVisualStyles = false;
        _grid.ColumnHeadersDefaultCellStyle.BackColor = Color.FromArgb(74, 24, 32);
        _grid.ColumnHeadersDefaultCellStyle.ForeColor = Color.FromArgb(232, 197, 71);
        _grid.DefaultCellStyle.BackColor = Color.FromArgb(42, 16, 22);
        _grid.DefaultCellStyle.ForeColor = Color.FromArgb(246, 238, 230);
        _grid.DefaultCellStyle.SelectionBackColor = Color.FromArgb(107, 42, 52);
    }
}
