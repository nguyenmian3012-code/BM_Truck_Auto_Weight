using System.IO.Ports;

namespace BmCancomp;

public sealed class FrameEventArgs : EventArgs
{
    public required string Port { get; init; }
    public required string Raw { get; init; }
    public required DateTime Ts { get; init; }
}

public sealed class ListenPort : IDisposable
{
    readonly PortSettings _cfg;
    SerialPort? _sp;
    readonly object _gate = new();
    string _buf = "";

    public event EventHandler<FrameEventArgs>? Frame;
    public event EventHandler<string>? Status;
    public bool IsOpen => _sp?.IsOpen == true;
    public string PortName => _cfg.Port;

    public ListenPort(PortSettings cfg) => _cfg = cfg;

    public void Open()
    {
        Close();
        var parity = Enum.Parse<Parity>(_cfg.Parity, true);
        var stop = Enum.Parse<StopBits>(_cfg.StopBits, true);
        var hs = Enum.Parse<Handshake>(_cfg.Handshake, true);
        var sp = new SerialPort(_cfg.Port, _cfg.Baud, parity, _cfg.DataBits, stop)
        {
            Handshake = hs,
            DtrEnable = _cfg.Dtr,
            RtsEnable = _cfg.Rts,
            ReadTimeout = 200,
            WriteTimeout = 200,
            NewLine = "\r",
            Encoding = System.Text.Encoding.ASCII,
        };
        sp.DataReceived += OnData;
        sp.ErrorReceived += (_, e) => Status?.Invoke(this, $"lỗi {e.EventType}");
        try
        {
            sp.Open();
            sp.DtrEnable = _cfg.Dtr;
            sp.RtsEnable = _cfg.Rts;
            sp.Handshake = Handshake.None;
            _sp = sp;
            Status?.Invoke(this, $"mở {_cfg.Port} {_cfg.Baud} {_cfg.DataBits}{_cfg.Parity[0]}{(stop == StopBits.One ? "1" : stop.ToString())}");
        }
        catch (Exception ex)
        {
            sp.Dispose();
            Status?.Invoke(this, $"không mở {_cfg.Port}: {ex.Message}");
            throw;
        }
    }

    void OnData(object? sender, SerialDataReceivedEventArgs e)
    {
        SerialPort? sp;
        lock (_gate) sp = _sp;
        if (sp == null || !sp.IsOpen) return;
        string chunk;
        try { chunk = sp.ReadExisting(); }
        catch { return; }
        if (string.IsNullOrEmpty(chunk)) return;
        lock (_gate)
        {
            _buf += chunk;
            while (true)
            {
                var iCr = _buf.IndexOf('\r');
                var iLf = _buf.IndexOf('\n');
                var iEq = _buf.IndexOf('=');
                var cut = int.MaxValue;
                if (iCr >= 0) cut = Math.Min(cut, iCr);
                if (iLf >= 0) cut = Math.Min(cut, iLf);
                if (iEq >= 0) cut = Math.Min(cut, iEq);
                if (cut == int.MaxValue)
                {
                    if (_buf.Length > 256) _buf = _buf[^80..];
                    break;
                }
                var line = _buf[..(cut + (iEq == cut ? 1 : 0))];
                _buf = _buf[(cut + 1)..];
                var raw = line.Trim('\r', '\n', '\0', ' ');
                if (raw.Length == 0) continue;
                Frame?.Invoke(this, new FrameEventArgs { Port = _cfg.Port, Raw = raw, Ts = DateTime.Now });
            }
        }
    }

    public void Close()
    {
        lock (_gate)
        {
            if (_sp == null) return;
            try { _sp.DataReceived -= OnData; } catch { }
            try { if (_sp.IsOpen) _sp.Close(); } catch { }
            try { _sp.Dispose(); } catch { }
            _sp = null;
            _buf = "";
        }
        Status?.Invoke(this, $"đóng {_cfg.Port}");
    }

    public void Dispose() => Close();
}
