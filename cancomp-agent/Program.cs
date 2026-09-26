using System.Text;
using BmCancomp;

Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
ApplicationConfiguration.Initialize();
Application.SetHighDpiMode(HighDpiMode.PerMonitorV2);

var cfg = AppConfig.Load();
var store = new SqliteStore(AppConfig.DataDir);
store.Init();
Application.Run(new MainForm(cfg, store));
