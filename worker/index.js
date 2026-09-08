function page() {
  return [
    "<!doctype html>",
    '<html lang="vi">',
    "<head>",
    '<meta charset="utf-8" />',
    '<meta name="viewport" content="width=device-width,initial-scale=1" />',
    "<title>BM Cân Xe Tự Động</title>",
    '<link rel="preconnect" href="https://fonts.googleapis.com" />',
    '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Be+Vietnam+Pro:wght@400;500;600&display=swap" rel="stylesheet" />',
    "<style>",
    ":root{--bg:#12150f;--fg:#eef2e8;--card:#1a1f18;--muted:#8b9384;--line:#2e362c;--accent:#b7c9a3;--plate:#f0d24a;--warn:#d4b56a;--bad:#d67a6f}",
    "*{box-sizing:border-box}",
    'html,body{margin:0;min-height:100dvh;background:var(--bg);color:var(--fg);font-family:"Be Vietnam Pro",system-ui,sans-serif}',
    'h1,h2{font-family:"Barlow Condensed",sans-serif;font-weight:700;letter-spacing:.02em;margin:0}',
    ".wrap{max-width:980px;margin:0 auto;padding:28px 18px 80px}",
    ".kicker{font-size:12px;letter-spacing:.28em;text-transform:uppercase;color:var(--accent);font-weight:600}",
    ".sub{color:var(--muted);font-size:14px;margin-top:8px;line-height:1.5}",
    ".card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}",
    ".row{display:flex;gap:10px;flex-wrap:wrap}",
    "input,select,button{font:inherit;border-radius:12px;border:1px solid var(--line);background:#232a20;color:var(--fg);padding:12px 14px;min-height:44px}",
    "button{cursor:pointer;background:var(--accent);color:#141910;font-weight:600;border:0}",
    "button.ghost{background:#232a20;color:var(--fg);border:1px solid var(--line)}",
    "button.plate{background:var(--plate)}",
    "nav{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:18px 0}",
    "nav button{background:#232a20;color:var(--muted)}",
    "nav button.on{background:var(--accent);color:#141910}",
    '.num{font-family:"Barlow Condensed",sans-serif;font-size:42px;color:var(--plate);letter-spacing:.08em}',
    ".kpi{flex:1;min-width:140px}",
    '.kpi b{display:block;font-size:28px;font-family:"Barlow Condensed",sans-serif}',
    ".grid{display:grid;gap:12px}",
    "@media(min-width:720px){.grid.two{grid-template-columns:1fr 1fr}}",
    "table{width:100%;border-collapse:collapse;font-size:13px}",
    "th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line)}",
    ".lock{max-width:420px;margin:12vh auto}",
    ".err{color:var(--bad);font-size:13px}",
    ".warn{color:var(--warn)}",
    "</style></head><body><div id='app'></div>",
    "<script>",
    "const KEY='BinhMinh-CanXe';",
    "const state={unlocked:sessionStorage.getItem('bm-ok')===KEY,err:false,tab:'can',plate:'51C-248.19',conf:91,dir:'IN',kg:18420,cargo:'Củ mì tươi',starch:27.6,sessions:[{t:'06:12',p:'51C-248.19',d:'IN',kg:18420,q:28.1},{t:'07:40',p:'60C-127.88',d:'OUT',kg:6120,q:27.4},{t:'09:05',p:'8KXM492',d:'IN',kg:22100,q:'\u2014'}]};",
    "function render(){",
    "const root=document.getElementById('app');",
    "if(!state.unlocked){",
    "root.innerHTML='<div class=\"wrap lock\"><p class=\"kicker\">Bình Minh</p><h1 style=\"font-size:48px;margin-top:6px\">Mã trạm</h1><p class=\"sub\">canxe.redtigerhead.com \u2014 nhập secret key trước khi vào bàn cân.</p><form class=\"card\" style=\"margin-top:22px;display:grid;gap:10px\" id=\"lock\"><input type=\"password\" autocomplete=\"off\" placeholder=\"Secret key\" id=\"pin\" /><p class=\"'+(state.err?'err':'sub')+'\">'+(state.err?'Sai mã trạm.':'Bản thử: BinhMinh-CanXe \u2014 đổi trước khi phát hành.')+'</p><button type=\"submit\">Vào trạm</button></form></div>';",
    "document.getElementById('lock').onsubmit=function(e){e.preventDefault();var v=document.getElementById('pin').value.trim();if(v!==KEY){state.err=true;render();return;}sessionStorage.setItem('bm-ok',KEY);state.unlocked=true;render();};",
    "return;}",
    "root.innerHTML='<div class=\"wrap\"><p class=\"kicker\">Bình Minh</p><h1 style=\"font-size:44px\">BM Cân Xe Tự Động</h1><p class=\"sub\">Hệ thống chụp hình, lưu biển số xe và cân nặng tự động thông minh, chuyên nghiệp.</p><nav><button data-tab=\"can\">Cân xe</button><button data-tab=\"cam\">Camera</button><button data-tab=\"q\">Thử mẫu</button><button data-tab=\"r\">Sổ ngày</button></nav><div id=\"desk\"></div></div>';",
    "root.querySelectorAll('nav button').forEach(function(b){if(b.getAttribute('data-tab')===state.tab)b.className='on';b.onclick=function(){state.tab=b.getAttribute('data-tab');render();};});",
    "var desk=document.getElementById('desk');",
    "if(state.tab==='can'){",
    "desk.innerHTML='<div class=\"grid two\"><div class=\"card\"><p class=\"kicker\">Biển số</p><div class=\"num\">'+state.plate+'</div><p class=\"warn\">Tin cậy '+state.conf+'% \u2014 dưới 95% phải xác nhận thủ công.</p></div><div class=\"card\"><p class=\"kicker\">Cân</p><div class=\"num\">'+state.kg.toLocaleString('vi-VN')+' kg</div><p class=\"sub\">'+state.cargo+' \u00b7 khớp binhminh_data khi ghi sổ</p><button class=\"plate\" id=\"ok\" style=\"margin-top:12px\">Xác nhận & ghi sổ</button></div></div>';",
    "document.getElementById('ok').onclick=function(){alert('Đã ghi sổ '+state.plate+' / '+state.dir+' / '+state.kg+' kg');};",
    "}else if(state.tab==='cam'){",
    "desk.innerHTML='<div class=\"grid two\"><div class=\"card\"><p class=\"kicker\">Cam trước</p><p class=\"sub\">JPEG xám, max 640px. Tự chụp lại nếu nét thấp.</p></div><div class=\"card\"><p class=\"kicker\">Cam sau</p><p class=\"sub\">Đối chiếu biển. Lệch thì pending_confirm.</p></div></div>';",
    "}else if(state.tab==='q'){",
    "desk.innerHTML='<div class=\"card\"><p class=\"kicker\">RS232 \u00b7 không sửa được</p><div class=\"num\">'+state.starch.toFixed(1)+'%</div><p class=\"sub\">Gán điểm tinh bột vào xe đang IN.</p><div class=\"row\" style=\"margin-top:12px\"><button class=\"ghost\">51C-248.19</button><button class=\"ghost\">8KXM492</button></div></div>';",
    "}else{",
    "var rows=state.sessions.map(function(s){return '<tr><td>'+s.t+'</td><td>'+s.p+'</td><td>'+s.d+'</td><td>'+s.kg.toLocaleString('vi-VN')+'</td><td>'+s.q+'</td></tr>';}).join('');",
    "desk.innerHTML='<div class=\"row\"><div class=\"card kpi\"><span class=\"sub\">Tấn vào</span><b>89.2</b></div><div class=\"card kpi\"><span class=\"sub\">Tấn ra</span><b>41.6</b></div><div class=\"card kpi\"><span class=\"sub\">Điểm TB</span><b>27.8%</b></div></div><div class=\"card\" style=\"margin-top:12px\"><table><thead><tr><th>Giờ</th><th>Biển</th><th>Hướng</th><th>Kg</th><th>%</th></tr></thead><tbody>'+rows+'</tbody></table></div>';",
    "}}",
    "render();",
    "</script></body></html>",
  ].join("\n");
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        app: "bm-can-xe",
        host: env.STATION_HOST || "canxe.redtigerhead.com",
      });
    }
    return new Response(page(), {
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "no-store",
      },
    });
  },
};
