# BM Cân Xe Tự Động

Repo **gốc**. Cloudflare Worker `bm-can-xe` nối đây.

- Production: https://canxe.redtigerhead.com
- Worker: `bm-can-xe` (Workers & Pages)
- Staging branch: `app/canxe`
- **Không** dùng repo copy https://github.com/nguyenmian3012-code/bm-can-xe (Cloudflare bot import)

## Tối nay — cổng Cloudflare

1. dash.cloudflare.com → thanh trái **bm-can-xe** (Workers), không bấm Workers AI.
2. Tab **Domains** → Enable **workers.dev** nếu đang Disable.
3. Cùng tab → **Add custom domain** → `canxe.redtigerhead.com` → đợi **Active**.
4. Không Add record DNS type HTTPS.
5. Settings → Variables and Secrets → Secret `STATION_KEY` (mã nhà máy).
6. Tab **Access** → chỉ email nhà máy.

Mã thử tạm: `BinhMinh-CanXe` — đổi trước khi phát hành.

`main` chỉ là cổng (Mã trạm + 4 tab). App cân đầy đủ chưa merge.
