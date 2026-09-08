# BM Cân Xe Tự Động — nhánh `app/canxe`

Host production: https://canxe.redtigerhead.com  
**Không dùng Pages / không Upload static files.**

## Màn Cloudflare "Make something new"

Bấm **Continue with GitHub** (ô có chấm xanh). Không chọn:

- Upload your static files
- Start with Hello World
- Select a template
- Connect GitLab

Sau khi GitHub hỏi quyền Cloudflare:

1. Chọn repo `BM_Truck_Auto_Weight`
2. Production branch: `app/canxe`
3. Project name: `bm-can-xe`
4. Nếu hỏi Worker vs Pages → **Worker**
5. Deploy xong: Settings → Domains & Routes → Custom Domain `canxe.redtigerhead.com`

Cloudflare tự tạo CNAME `canxe` (Proxied) + SSL. Không thêm tay record type HTTPS.

## Mã trạm

- Thử: `BinhMinh-CanXe` — đổi trước khi phát hành
- Trên `canxe.redtigerhead.com` luôn hỏi mã
- Thêm Cloudflare Access (Zero Trust) cho email nhà máy

Không merge `main` cho đến khi domain mở được.
