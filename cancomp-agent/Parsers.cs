using System.Globalization;
using System.Text.RegularExpressions;

namespace BmCancomp;

public static class KingbirdParser
{
    static readonly Regex Num = new(@"[-+]?\d+(?:[.,]\d+)?", RegexOptions.Compiled);

    public static bool TryParse(string raw, out double kg, out bool? deviceStable)
    {
        kg = 0;
        deviceStable = null;
        if (string.IsNullOrWhiteSpace(raw)) return false;
        var line = raw.Trim();
        if (line.Contains("OL", StringComparison.OrdinalIgnoreCase) ||
            line.Contains("ERR", StringComparison.OrdinalIgnoreCase) ||
            line.Contains("-----"))
            return false;

        var m = Num.Match(line.Replace(',', '.'));
        if (!m.Success) return false;
        if (!double.TryParse(m.Value.Replace(',', '.'), NumberStyles.Float, CultureInfo.InvariantCulture, out var v))
            return false;
        kg = v;
        if (Regex.IsMatch(line, @"\bST\b|\bS\b|,S\b|\*")) deviceStable = true;
        if (Regex.IsMatch(line, @"\bUS\b|\bU\b|,U\b")) deviceStable = false;
        return true;
    }
}

public static class StarchParser
{
    public static bool TryParse(string raw, out double pct)
    {
        pct = 0;
        if (string.IsNullOrWhiteSpace(raw)) return false;
        var line = raw.Trim();
        var eq = Regex.Match(line, @"(\d{4,8})\s*=");
        if (eq.Success)
        {
            if (!int.TryParse(eq.Groups[1].Value, out var n)) return false;
            if (n == 0) { pct = 0; return true; }
            pct = ScaleSixDigits(n);
            return pct >= 0;
        }
        var m = Regex.Match(line.Replace(',', '.'), @"(\d+(?:\.\d+)?)");
        if (!m.Success) return false;
        if (!double.TryParse(m.Value, NumberStyles.Float, CultureInfo.InvariantCulture, out var v))
            return false;
        if (v > 100 && v <= 1000) v /= 10;
        if (v > 1000 && v <= 10000) v /= 100;
        if (v > 10000 && v <= 100000) v /= 1000;
        pct = v;
        return true;
    }

    static double ScaleSixDigits(int n)
    {
        if (n >= 10000) return n / 1000.0;
        if (n >= 1000) return n / 100.0;
        if (n >= 100) return n / 10.0;
        return n;
    }
}

public sealed class PlateauFilter
{
    readonly double _floor, _minPeak, _band, _windowSec, _max;
    readonly Queue<(DateTime ts, double v)> _win = new();
    bool _emitted;

    public PlateauFilter(double floor, double minPeak, double band, double windowSec, double max)
    {
        _floor = floor; _minPeak = minPeak; _band = band; _windowSec = windowSec; _max = max;
    }

    public bool OnSample(DateTime ts, double value, out double plateau)
    {
        plateau = 0;
        if (value < 0 || value > _max) return false;
        if (value <= _floor) { _win.Clear(); _emitted = false; return false; }
        if (value < _minPeak) return false;
        _win.Enqueue((ts, value));
        var cut = ts.AddSeconds(-_windowSec);
        while (_win.Count > 0 && _win.Peek().ts < cut) _win.Dequeue();
        if (_emitted) return false;
        if (_win.Count < 3) return false;
        if ((_win.Last().ts - _win.First().ts).TotalSeconds < _windowSec * 0.9) return false;
        var min = _win.Min(x => x.v);
        var max = _win.Max(x => x.v);
        if (max - min > _band) return false;
        plateau = Math.Round(_win.Average(x => x.v), 2);
        _emitted = true;
        return true;
    }

    public void Reset() { _win.Clear(); _emitted = false; }
}
