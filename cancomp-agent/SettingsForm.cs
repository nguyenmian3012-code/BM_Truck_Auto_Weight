using System.IO.Ports;

namespace BmCancomp;

public sealed class SettingsForm : Form
{
    public SettingsForm(AppConfig cfg)
    {
        Text = "Cài đặt admin — BM CANcomp";
        Width = 640; Height = 640;
        StartPosition = FormStartPosition.CenterParent;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false; MinimizeBox = false;
        BackColor = Color.FromArgb(42, 10, 18);
        ForeColor = Color.FromArgb(246, 238, 230);
        Font = new Font("Segoe UI", 10f);

        var ports = SerialPort.GetPortNames();
        if (ports.Length == 0) ports = new[] { cfg.Scale.Port, cfg.Starch.Port };

        var y = 16;
        void AddLabel(string t) { Controls.Add(new Label { Text = t, AutoSize = true, Location = new Point(24, y) }); }
        TextBox AddBox(string v, int w = 360)
        {
            var tb = new TextBox { Text = v, Width = w, Location = new Point(220, y - 4) };
            Controls.Add(tb); y += 34; return tb;
        }
        ComboBox AddCombo(string v, string[] items)
        {
            var cb = new ComboBox { Width = 180, Location = new Point(220, y - 4), DropDownStyle = ComboBoxStyle.DropDown };
            cb.Items.AddRange(items); cb.Text = v; Controls.Add(cb); y += 34; return cb;
        }

        AddLabel("Mã trạm"); var station = AddBox(cfg.StationId);
        AddLabel("URL ingest"); var url = AddBox(cfg.IngestUrl);
        AddLabel("STATION_KEY"); var key = AddBox(cfg.StationKey); key.UseSystemPasswordChar = true;
        AddLabel("PIN admin"); var pin = AddBox(cfg.AdminPin);
        y += 8; AddLabel("— Cầu cân Kingbird —"); y += 28;
        AddLabel("COM cân"); var sPort = AddCombo(cfg.Scale.Port, ports);
        AddLabel("Baud cân"); var sBaud = AddCombo(cfg.Scale.Baud.ToString(), new[] { "1200", "2400", "4800", "9600", "19200" });
        AddLabel("Sàn / min đỉnh / ε kg"); var sFloor = AddBox($"{cfg.Scale.FloorKg};{cfg.Scale.MinPeakKg};{cfg.Scale.BandKg}");
        y += 8; AddLabel("— Máy bột 1200 8N1 —"); y += 28;
        AddLabel("COM bột"); var tPort = AddCombo(cfg.Starch.Port, ports);
        AddLabel("Baud bột"); var tBaud = AddCombo(cfg.Starch.Baud.ToString(), new[] { "1200", "2400", "4800", "9600" });
        AddLabel("Sàn / min đỉnh / ε %"); var tFloor = AddBox($"{cfg.Starch.FloorPct};{cfg.Starch.MinPeakPct};{cfg.Starch.BandPct}");

        Controls.Add(new Label {
            Text = "Listen-only: không RTS/DTR, không software flow, không ghi byte.",
            Location = new Point(24, y + 8), AutoSize = true,
            ForeColor = Color.FromArgb(201, 180, 173),
        });

        var save = new Button {
            Text = "Lưu", Width = 140, Height = 40, Location = new Point(220, 540),
            BackColor = Color.FromArgb(212, 175, 55), ForeColor = Color.FromArgb(42, 10, 18), FlatStyle = FlatStyle.Flat,
        };
        save.Click += (_, _) =>
        {
            cfg.StationId = station.Text.Trim();
            cfg.IngestUrl = url.Text.Trim();
            cfg.StationKey = key.Text.Trim();
            if (!string.IsNullOrWhiteSpace(pin.Text)) cfg.AdminPin = pin.Text.Trim();
            cfg.ListenOnly = true;
            cfg.Scale.Port = sPort.Text.Trim();
            if (int.TryParse(sBaud.Text, out var sb)) cfg.Scale.Baud = sb;
            cfg.Scale.Dtr = false; cfg.Scale.Rts = false; cfg.Scale.Handshake = "None"; cfg.Scale.Parity = "None"; cfg.Scale.DataBits = 8;
            ParseTriple(sFloor.Text, out var a, out var b, out var c);
            if (a > 0) cfg.Scale.FloorKg = a; if (b > 0) cfg.Scale.MinPeakKg = b; if (c > 0) cfg.Scale.BandKg = c;
            cfg.Starch.Port = tPort.Text.Trim();
            if (int.TryParse(tBaud.Text, out var tbv)) cfg.Starch.Baud = tbv;
            cfg.Starch.Dtr = false; cfg.Starch.Rts = false; cfg.Starch.Handshake = "None"; cfg.Starch.Parity = "None"; cfg.Starch.DataBits = 8;
            ParseTriple(tFloor.Text, out var d, out var e, out var f);
            if (d > 0) cfg.Starch.FloorPct = d; if (e > 0) cfg.Starch.MinPeakPct = e; if (f > 0) cfg.Starch.BandPct = f;
            DialogResult = DialogResult.OK;
        };
        Controls.Add(save);
    }

    static void ParseTriple(string s, out double a, out double b, out double c)
    {
        a = b = c = 0;
        var p = s.Split(new[] { ';', ',', ' ' }, StringSplitOptions.RemoveEmptyEntries);
        if (p.Length > 0) double.TryParse(p[0], out a);
        if (p.Length > 1) double.TryParse(p[1], out b);
        if (p.Length > 2) double.TryParse(p[2], out c);
    }
}
