using System.Text.Json;
using System.Text.Json.Serialization;

namespace BmCancomp;

public sealed class PortSettings
{
    public string Port { get; set; } = "COM4";
    public int Baud { get; set; } = 1200;
    public int DataBits { get; set; } = 8;
    public string Parity { get; set; } = "None";
    public string StopBits { get; set; } = "One";
    public string Handshake { get; set; } = "None";
    public bool Dtr { get; set; }
    public bool Rts { get; set; }
    public double FloorKg { get; set; } = 80;
    public double MinPeakKg { get; set; } = 400;
    public double BandKg { get; set; } = 20;
    public double WindowSec { get; set; } = 2;
    public double MaxKg { get; set; } = 120000;
    public double FloorPct { get; set; } = 0.05;
    public double MinPeakPct { get; set; } = 5;
    public double BandPct { get; set; } = 0.2;
    public double MaxPct { get; set; } = 80;
}

public sealed class AppConfig
{
    public string StationId { get; set; } = "BinhMinh-CanXe";
    public string IngestUrl { get; set; } = "https://canxe.redtigerhead.com/api/ingest";
    public string StationKey { get; set; } = "";
    public string AdminPin { get; set; } = "2580";
    public bool ListenOnly { get; set; } = true;
    public PortSettings Scale { get; set; } = new();
    public PortSettings Starch { get; set; } = new() { Port = "COM5" };

    static readonly JsonSerializerOptions JsonOpt = new()
    {
        PropertyNameCaseInsensitive = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        ReadCommentHandling = JsonCommentHandling.Skip,
        AllowTrailingCommas = true,
    };

    public static string AppDir =>
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.CommonApplicationData), "BmCancomp");

    public static string DataDir => Path.Combine(AppDir, "data");
    public static string ConfigPath => Path.Combine(AppDir, "appsettings.json");

    public static AppConfig Load()
    {
        Directory.CreateDirectory(AppDir);
        Directory.CreateDirectory(DataDir);
        var bundled = Path.Combine(AppContext.BaseDirectory, "appsettings.json");
        if (!File.Exists(ConfigPath) && File.Exists(bundled))
            File.Copy(bundled, ConfigPath);
        if (!File.Exists(ConfigPath))
        {
            var fresh = new AppConfig();
            fresh.Save();
            return fresh;
        }
        var text = File.ReadAllText(ConfigPath);
        return JsonSerializer.Deserialize<AppConfig>(text, JsonOpt) ?? new AppConfig();
    }

    public void Save()
    {
        Directory.CreateDirectory(AppDir);
        File.WriteAllText(ConfigPath, JsonSerializer.Serialize(this, JsonOpt));
    }
}

public sealed class IngestPayload
{
    public string Id { get; set; } = Guid.NewGuid().ToString("N");
    public string Source { get; set; } = "";
    public string StationId { get; set; } = "";
    public double? Kg { get; set; }
    public double? StarchPct { get; set; }
    public bool Stable { get; set; } = true;
    public string Ts { get; set; } = DateTimeOffset.Now.ToString("o");
    public string Raw { get; set; } = "";
}

public sealed class StoredEvent
{
    public long RowId { get; set; }
    public string Id { get; set; } = "";
    public string Source { get; set; } = "";
    public double? Kg { get; set; }
    public double? StarchPct { get; set; }
    public string Ts { get; set; } = "";
    public string Raw { get; set; } = "";
    public string Sync { get; set; } = "queued";
}
