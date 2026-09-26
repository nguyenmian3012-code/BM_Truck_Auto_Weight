using System.Net.Http.Json;
using System.Text.Json;

namespace BmCancomp;

public sealed class IngestClient
{
    readonly HttpClient _http = new() { Timeout = TimeSpan.FromSeconds(20) };
    static readonly JsonSerializerOptions JsonOpt = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull,
    };

    public async Task<(bool ok, string msg)> SendAsync(AppConfig cfg, IngestPayload p, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(cfg.StationKey))
            return (false, "chưa nhập STATION_KEY (admin)");
        p.StationId = cfg.StationId;
        using var req = new HttpRequestMessage(HttpMethod.Post, cfg.IngestUrl);
        req.Headers.TryAddWithoutValidation("X-Station-Key", cfg.StationKey);
        req.Content = JsonContent.Create(p, options: JsonOpt);
        try
        {
            using var res = await _http.SendAsync(req, ct);
            var body = await res.Content.ReadAsStringAsync(ct);
            if ((int)res.StatusCode is >= 200 and < 300)
                return (true, $"{(int)res.StatusCode}");
            return (false, $"{(int)res.StatusCode} {Trim(body)}");
        }
        catch (Exception ex)
        {
            return (false, ex.Message);
        }
    }

    static string Trim(string s) => s.Length > 160 ? s[..160] : s;
}
