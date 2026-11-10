# Agent Delivery Status — 規格與兩輪交付設計

## 1. 契約、證據與範圍

- 規格 owner：architect；本次 card `t_021dff9f`、run `1`、board `agent-team`。根驗收 card `t_44704c9f`；獨立 preflight card `t_38c2fb29`。識別來自原生 `kanban_show`，不是任務已完成的宣告。
- 規範輸入：`goal-contract.md`（全文）；來源紀錄：`evidence/native-admission.json`，其 voice_origin 明載 user-declared live spoken delegation。本規格未取得音訊/session 的獨立證據，不把 CLI/API bootstrap、文字 marker 當麥克風測試，也不要求重測已確認收音播放。
- 本卡只寫 `spec.md`、`acceptance-matrix.md`；不實作、建 repo、發 Issue/PR、調整 Dispatcher、建立任務或碰 VM。workspace 不是 Git repo（`git status --short` exit 128），故本次沒有 commit/PR head。
- 產品：一頁只讀查詢 + `/healthz` + `/version`，不含 DB、登入、寫入 API、GitHub token、Kanban 副本、工作佇列、第二 Dispatcher、監控控制台或 deployment 按鈕。
- 外部目的 repo 固定為 **PRIVATE `timmypai/agent-delivery-status`**；是否存在、可用權限、CI 預算、registry、Oracle host/address/port/path 尚須 preflight 證據，不在此猜測。架構決策不構成額外授權。

## 2. 最小架構與決策

建議 Python stdlib HTTP server、單一 Docker image、無外部 runtime 套件；實作可用等價小型方案，但不得改動下列 HTTP/metadata 契約。單程序載入經驗證的 immutable build metadata，讀取每次部署的唯讀 receipt，服務 HTML 與 JSON。對 GitHub、Kanban 無 runtime 網路呼叫；私人連結由使用者已登入的瀏覽器開啟，未登入可得到 GitHub 404/登入要求，不由應用代理認證。

界線：build producer 負責 commit/build metadata；DevOps 負責部署 receipt 與實際 image/HTTP 回讀；應用只報本機狀態與證據入口；Reviewer/根驗收負責外部真假與是否可交付。`healthz=ok` 不是 CI/review/部署驗收 PASS。

容器：非 root、read-only filesystem、無 privileged/host network/host PID/credential mount/Docker socket；僅單一服務 port（容器內 8080）。資源目標 CPU <=0.5、memory <=128MiB、pids <=64，實際主機可用量不足則 preflight 阻擋，不調大既有服務配額。host port、應用目錄、容器/network 名稱、入口及允許客戶端由 DevOps 預檢後明確記錄；不假設公開 IP、TLS、DNS 或反向代理授權。不能滿足隔離時不部署。

## 3. 介面與資料模型（v1 = 1.0.0）

### HTTP

| 路徑 | 成功 | 失敗/限制 |
|---|---|---|
| `GET /` | 200 `text/html; charset=utf-8`；同源顯示 release、完整 commit、build time、deployment id、健康與 Issue/PR/CI 連結 | metadata 無效不得顯示綠色正常；顯示 unavailable 並 503，或啟動失敗 |
| `GET /healthz` | 200 `application/json`，`{"status":"ok","checks":{"build_metadata":"ok","deployment_receipt":"ok"}}` | receipt 缺失/格式或 commit 不符：503，status=`unavailable`，失敗 check=`invalid`；不洩漏檔案/stack/環境資訊 |
| `GET /version` | 200 `application/json`；下述 schema | metadata/receipt 無效 503 `{"error":"metadata_unavailable"}`，不退回假版本 |
| 未定義路徑 | 404 | 不讀任意檔案、不得 path traversal |
| 非 GET/HEAD 方法 | 405 + `Allow: GET, HEAD` | 不改狀態；HEAD 與 GET 同 status/headers、無 body |

所有回應 `Cache-Control: no-store`，健康不能由瀏覽器舊快取冒充；不開跨來源 CORS。HTML 的健康由當次 `/healthz` 同一檢查函式求得，標為「本機健康（非交付驗收）」；可只手動重新整理，無需 background polling。HTML escape 所有值；固定 GitHub URL allowlist，外開連結 `rel="noopener noreferrer"`；建議 CSP 限 same-origin 並禁 frame/object。不得在 HTML/JSON/logs 回傳 hostname、內網 IP、token、環境變數或 auth 檔內容。

### `/version` 必要欄位與來源

| 欄位 | 型別/約束 | 真實來源 |
|---|---|---|
| `schema_version` | integer `1` | API schema，v2 additive 不升 major |
| `release` | string `1.0.0`（第二輪 `1.0.1`） | repo release 檔，CI 檢查 |
| `commit` | 完整小寫 40 hex Git SHA | CI 實際 checkout 的 `git rev-parse HEAD`，不可只截短或手填成功值 |
| `built_at` | UTC RFC3339 | image build producer 記錄建置時間 |
| `repository_url` | `https://github.com/timmypai/agent-delivery-status` | 固定核准 repo |
| `evidence.issue_url` | 該 repo `/issues/<positive integer>` | 已建立且 API 回讀的本輪 Issue |
| `evidence.pr_url` | 該 repo `/pull/<positive integer>` | 已 API 回讀且 head=commit 的本輪 PR |
| `evidence.ci_url` | 該 repo `/actions/runs/<positive integer>` | build 所在真實 run URL；CI 最終 conclusion 由外部另驗 |
| `deployment.id` | 非空、不含秘密的 deployment 識別字 | DevOps 本輪 receipt；不可用來充當 Kanban 狀態 |
| `deployment.deployed_at` | UTC RFC3339 | DevOps 實際啟動本輪容器時間 |

build metadata 是 CI 生成並 bake 到 image 的 JSON，包含 release/commit/built_at/repository_url/evidence；應用不可用 runtime env 覆寫 commit。部署 receipt 是唯一 app-specific 唯讀 mount 的 JSON，包含 `id,deployed_at,commit,image_digest`；其中 commit 必須等於 baked commit，image_digest 必須為 `sha256:` 加 64 hex。`/version` 不需公開 image_digest，但 DevOps 的驗收報告必須保留並核對。應用無法單靠 receipt 證明實際 image digest，故 receipt 自述永不取代 `docker inspect` 證據。

JSON parse 邊界拒絕缺欄、錯型、無效 SHA/time/URL、credentials in URL、非 allowlist host/path（含 javascript URL）、receipt mismatch。初始化失敗可直接非零退出；已運行時 receipt 遺失或損壞須在每次健康/版本請求檢查並回 503，不沿用舊綠燈。build metadata 可在啟動時 validate/cache，receipt 每次讀取有固定大小上限（64KiB），不接受客戶端指定路徑。

**非循環 provenance：** image 不內嵌自己的 digest（內容自指不可能）；CI run URL 可在 build 期間取得，但不能 bake「該 run 已成功」。digest 於 image 完成後取得並交給部署 receipt。頁面提供證據連結而不是硬編碼「CI PASS」。

## 4. 版本一致性與交付閘門

統一使用 **reviewed PR author head C** 作 deployment commit，不默認使用 Actions `pull_request` synthetic merge SHA。CI checkout C；required checks 及 image build 必須針對 C（實際 checkout 和 check association 都留證）。Reviewer verdict 明指 C。若 merge/squash/rebase 後選擇另一 commit M，必須重新取得 M 的獨立 review、CI/image，再部署 M；不可把 C 的綠燈搬到 M。

交付證據鏈：`Issue -> PR head C -> independent verdict(C) -> required checks(C) -> build checkout C -> image OCI revision C + immutable digest D -> registry/transfer D -> Oracle container image D -> HTTP /version.commit C`。DevOps 分別保留 `docker image inspect` 的 revision、RepoDigest、container `.Image` 與 image ID 的連結；多架構 manifest digest 與 platform digest 不直接混比，報告完整對照。不得只用 mutable tag（如 latest）判定。

CI 必需檢查最少固定為 `test`、`docker-smoke`（在 repo 初始化/設定時確認實際 check 名稱）；required set 必須非空且所有命名檢查在 exact head completed/success。skipped、neutral、cancelled、pending、解析失敗、無權限、不完整分頁、過期 head 皆不接受。Docker smoke 真實啟容器並驗 HTTP/metadata/非 root/無 socket mount；測試包含負向案例。

若無 registry 安全預算或權限，DevOps 可在同一核准 host 範圍用 Docker save/load 傳送已測 image，保存 image ID + archive SHA256 並驗收前後一致；不得聲稱不存在的 registry digest。此替代仍需確保 content-addressed image ID、OCI revision、CI artifact 相符，並在根驗收明記沒有 registry publication。若既定後續卡強制 registry，需該 gate 取得授權而非自行降標。

## 5. 兩輪交付與相容性

- **v1 1.0.0：** 完成第 3 節。真實 Issue/PR/CI/Docker/Oracle 回讀及獨立審查後，根紀錄首次完整交付的 C1/D1、HTTP 與角色證據。
- **v2 1.0.1：** 在 v1 已實際驗收後由既有 controller/Dispatcher 自動接續；新增頁面「查看此部署的原始碼」連結，`GET /version` additive `source_url`，嚴格等於 `repository_url + '/commit/' + commit`。這讓使用者從當前版本直達具體原始碼，非只改版本字串；不加外部 runtime 呼叫、DB、權限、費用或 infrastructure。
- v2 使用新的真實 Issue/PR、不同 commit C2、獨立 review(C2)、CI(C2)、image D2、Oracle 部署與 HTTP 比對；保留所有 v1 既有欄位/語意，舊 client 可忽略新欄。單測驗 exact URL、HTML escape、安全 scheme，CI regression 重跑全部 v1 案例。C2 != C1、D2 != D1，不能只更新 receipt。
- 不做資料遷移；無 DB。rollback 使用上一個已驗 image 和對應 receipt，v2->v1 客戶端必須允許 source_url 缺省。

## 6. 失敗、回滾與有限重試

preflight -> implemented -> independently-reviewed(C) -> CI-passed(C) -> deployed(D) -> externally-verified(C,D) 是證據關卡，不是另一套任務狀態 DB。每個 gate 在原生 Kanban 手續中留證，未滿足不得跳過；review/CI/merge/deployment/service health 分開報告。

- 先查 repo 重名/owner/private；401/403/網路失敗不算不存在。重送先回讀 repo/Issue/PR/container/部署 evidence，使用原生 card/run/release id 做冪等查找，不重複外部副作用。
- 對一般 review/CI 缺陷：原生 request_changes 回給實作者，記錄舊/新 SHA、失敗測試及原因；每輪 release 合計最多 **兩次**修復+重驗循環。上限仍失敗即附證據升級/重新規劃，不換模型無限重派、不改驗收。缺憑證/預算/host 授權走 genuine blocked；不得 retry 同一未變 capability denial。
- CI job timeout 建議 10min、每卡 runtime 明列且不超平台上限；controller 必須回讀實際 runtime/retry 設定，不能把此建議當成已強制。VM HTTP timeout 5s，最多 6 次、間隔 5s，每次記錄；失敗後停止推進並回滾，不無限輪詢。
- 佈署前保留上一版 immutable image+receipt，確認可用的 app-only rollback 指令與端口衝突；先驗 candidate 再替換 app-only container，允許 demo 短暫中斷，不要求零停機或改 Hermes proxy。health/commit/digest 不符立即回滾一次並重新核 HTTP 和舊 C/D。不得宣告 candidate 成功。
- 首次無舊版時移除/停用失敗的新 app-only container、撤回本 app 新增入口，留下「沒有已成功版本」，不得回滾 Hermes 或刪除共用 images/volumes。rollback 本身失敗立即 blocked 並附最小人工處理，不重啟主機/Hermes。
- rollback 負向演練用隔離 app candidate/本地 Docker，故意錯 receipt 或壞 health；不可為了證明返工而破壞既有服務。演練須標為 control test，不能偽稱真實 reviewer 退件。

## 7. 真實角色交接及可見性

僅既有原生 Dispatcher 執行派工。本卡不建立/調整 DAG；既有 controller 負責依授權接續，root 只作 final verifier。預期角色責任（非聲稱這些卡已存在）：

| 交接 | 輸入 | 必要輸出與 gate |
|---|---|---|
| Architect -> controller/Developer | goal-contract + 本兩份規格 | 本卡/run/絕對路徑；本地文件驗證，不冒充獨立 review |
| DevOps preflight -> controller | repo/CI/registry/host 授權 | 去敏預檢報告、budget 及隔離範圍；不足只阻該 gate，獨立本地工作可繼續 |
| controller -> Codex AppServer Developer | 真實 Issue、repo base SHA、此規格、限定 worktree/.git 範圍 | 原生 task/run、真實 AppServer session/結果、產品 commit、測試與 exit；不是 CLI bootstrap 截圖 |
| Developer -> independent Reviewer | exact C、diff、tests、provenance | 另一 profile verdict(C)；退回 request_changes 的原因與重驗證據 |
| approved head -> DevOps publication/CI | verdict(C)、最小授權、budget | 私有 repo/PR/check 回讀、C/D、workflow run、build log/artifact |
| CI -> DevOps deploy/verify | C/D、host/port/path、rollback | container image mapping、HTTP、舊/新版本、Hermes 不受影響證據 |
| v1 accepted -> v2 -> root | v1 完整證據及 scope 不變 | 真實 event-driven continuation、v2 全套證據、根分項判定 |

每次 comment 或原生 handoff metadata 至少包含：board/task/run/profile、upstream card/run/輸入路徑、output artifact 絕對路徑及必要 digest、commit/PR head/URL（不適用明寫）、測試命令/exit/result、獨立 verdict 來源及 SHA、CI run、部署版本及阻礙/下一步。不得填假 ID、假對話或 secrets；靜態 artifacts 只作證據，不替代 Kanban 真實狀態。

Desktop 第一輪需可定位 root `t_44704c9f`、本卡 `t_021dff9f`、preflight `t_38c2fb29` 以及後續真正 worker ID；驗收者以原生 UI/API 回讀驗證，非只看模型宣告。canonical Bot Chat 與 worker session 分開；若投遞摘要至既有 Bot，須有原生投遞 ID、target session、回讀及 UI attachment 可見證據，缺一標未驗證。不得因此建立新訊息通道/派工器或等待統一 Bot Chat 才做獨立可行工作。

## 8. 必須由後續 gate 解決的未知與安全預算

未取得：repo 真實存在/owner/private 回讀、workflow write/Actions 權限、Actions 剩餘免費額度/硬支出控制、registry 額度與授權、Oracle identity/SSH 方式/架構/port/path/資源/入口、現有 Hermes 基線、外部可達 HTTP 測點、canonical Chat 投遞/UI attachment、原始語音可回讀 locator。這些不是 spec 寫作阻礙，但不得據此宣告產品交付或猜 production 目的地。

Preflight 不讀秘密內容；只用任務授權 credential 的狀態/權限檢查。新 repo/Git metadata 的授權必須精確限定本工作範圍及有效期，不沿用撤回 pilot 目錄、不拓寬 sandbox。費用預算為新增支出 0；CI 免費剩餘額度和支出上限不可確認即停該 gate；不得買 runner/資源或改 billing。Docker socket 操作是高權限 host 能力，需核准其獨立應用操作範圍，絕不 mount 給 app。

## 9. 完成語義

`acceptance-matrix.md` 為每項 goal 的驗法。最終按「產品功能 / 首次完整交付 / 第二輪自動接續 / 可見性與自治 / 安全預算 / 未完成阻礙」逐項附實證。任何必需 goal 缺證據，根目標不能標完整成功。這張規格卡完成只表示設計與可執行驗收契約已交付，不表示 repo/CI/review/Oracle 或語音管線已驗證。
