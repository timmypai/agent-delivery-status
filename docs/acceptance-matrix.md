# Agent Delivery Status — 可執行驗收矩陣

規格依據：`spec.md`；需求逐條來源：`goal-contract.md` 行號。規格 card `t_021dff9f` / run `1`，root `t_44704c9f`，preflight `t_38c2fb29`，board `agent-team`。

**狀態語意：** 以下是後續角色必須執行的 acceptance contract，不是已執行測試清單。目前僅完成規格及文件結構核對；產品/CI/review/deploy/自治/UI/語音 locator 均未在本卡驗證。每列必須保存實際命令、exit、去敏原始回應/時間、card/run/owner、對應 C/D 與 artifact 路徑。無證據=未驗證；不能因工具 call 成功而 PASS。

## A. 全需求追溯

| ID | goal-contract 來源與必要目標 | 執行 owner / 驗收方法 | 可接受結果與必留證據 | 失敗時 |
|---|---|---|---|---|
| G01 | L5–7 真實小站驗證完整 delivery，不造新系統 | root 依下列全部必需列，串聯 v1/v2 的 card/run/Issue/PR/CI/image/HTTP；直接回讀每個外部 target | 兩輪完整、證據可定位；靜態文件不視為交付 | 根保持未完成，列出缺 gate |
| G02 | L11 一頁版本、健康、Issue/PR/CI 入口 | Developer+Reviewer：HTTP P1、瀏覽器檢查頁面與 `/version`、`/healthz` 對應；測私人連結 | 200、完整 SHA 與實際 build metadata 相同；健康標「本機」；三個真實連結；截圖/HTML/JSON/API 回讀 | request_changes；不可硬編碼綠燈 |
| G03 | L12 可機驗 health/version、真實 revision | Developer 單測 P2–P4，DevOps P5；對照 CI checkout / image label / container / HTTP | 正反例及 exact C/D 全部相符；不接受手改 env 假 SHA | CI 不通過或 app 回 503；禁止部署 |
| G04 | L13 無 DB/憑證/第二 Dispatcher/Kanban 替代 | Reviewer code/Dockerfile/dependency diff；DevOps 檢查 mount/network/process 與配置 diff（不讀 auth） | 無 DB/寫 API/credential、無 socket mount、無新增 dispatcher/queue；去敏 inspect | request_changes 或 capability block |
| G05 | L17–19 根與依賴為唯一真實狀態、角色接單可見 | controller/root 用原生 kanban_show 回讀完整依賴；Desktop 搜 root/真實 worker ID | 每卡 profile、body、run、結果/阻礙、依賴可回讀；截圖/原生結果。第一輪不得只給根卡 | 缺 worker/依賴證據不接受自治 |
| G06 | L20 每次交接有實際輸入輸出 | 各角色/root 對照所有實際 DAG edges 逐一回讀 handoff/comment/run | 每個 edge 有 task/run、exact input/output、artifact、C/URL/測試/verdict 或明確 N/A；無假 Bot dialogue | 補缺失證據，不能補造過去執行 |
| G07 | L21 canonical Chat 非 worker session；投遞須驗 attachment | controller 驗原生通知/投遞 target、message ID、讀回、Desktop UI attachment | Kanban 與 Bot session 分別記錄；若未投遞則如實標未完成，不推論 active=visible | 只停可見性 gate；不擋獨立本地工作 |
| G08 | L22 第一輪可定位 root+worker IDs | root 第一輪報告列原生真實 ID；Desktop 搜尋並回讀 assignee/run | 至少可定位 root `t_44704c9f`、architect `t_021dff9f`、preflight `t_38c2fb29`，以及實際 developer/reviewer/deploy 卡 | 不接受僅本對話「已交辦」 |
| G09 | L26 保留真人語音來源、不重測麥克風 | controller/root 連回原始 conversation/session/message locator（若系統保留），與 root/contract 對照 | `native-admission.json` 為 user-declared source，不冒充音訊；保存可回讀 locator；不以文字 marker/CLI 作 mic test | locator 不可取則標 provenance 未獨立驗證，窄範圍回報，不要求重新錄音 |
| G10 | L27 唯一 Dispatcher、Codex AppServer、獨立 review、各交付角色 | controller/root 讀原生 dispatch/claim/spawn/run 與 AppServer 真實執行 artifact；Reviewer 另一 profile | 指定 C 的開發 session/測試、獨立 verdict、DevOps、root 串接；Researcher 非必要無需湊數 | 缺 AppServer/獨立 reviewer 不 PASS；不得另開 scheduler |
| G11 | L28 有限 review/CI 返工與結果 | controller/Reviewer 保存真實 request_changes/修復/new C/重驗；若無真實缺陷，執行 P6 gate control 並明標演練 | 每 release <=2 修復/重驗；兩次仍失敗升級；不能假稱有真實退件。證明 gate 會拒絕 stale/failing head | 一般缺陷 request_changes；授權/預算缺失 blocked；不阻無依賴 ready 工作 |
| G12 | L29 不需逐卡命令/持續通話 | controller/root 依時間序讀 v1 完成通知、controller continuation、v2 claim/run/通知；核對其間用戶訊息 | v1->v2 是既有事件驅動，無逐卡指令；真實 notification/wake/後續動作，不只配置 | 只能報手動接續，自治項未通過 |
| G13 | L33 owner/private/查重與真實 Issue/PR | 授權 controller/DevOps 執行 E1，建立前讀 repo 存在性；每次寫後 exact target 回讀 | owner=`timmypai`、name=`agent-delivery-status`、private=true；Issue/PR 存在且本輪 head C；重名不覆蓋 | 401/403/網路錯不作不存在；不得盲建/公開 repo |
| G14 | L33 CLI auth 不代表 workflow/Actions/registry/VM 權限 | preflight 分項讀權限/免費額度/支出控制/registry 及 host 授權（不輸出 secrets） | 去敏報告分別記查證方法、時間、scope、有效期、結果；CLI 登入單項不夠 | 不足停對應 gate，提出最小授權 |
| G15 | L34 exact-version review/必需 CI/scope/外部回讀 | Reviewer/DevOps/root 執行 E2；required set 非空，reviewer != implementer | approved C=PR head=CI checkout/check association=image revision=HTTP；check 全 success；所有外部 writes 有 readback | stale、missing、skip、解析失敗均非 PASS |
| G16 | L35 真 Docker、Oracle HTTP、image digest 一致 | DevOps E3/P5，根從核准客戶端再次 HTTP 查詢；保存 host identity 去敏證據 | Oracle 實際 container Running；C/D/image ID mapping；真實 `healthz` 200、`version` C；不能只看 merged/build | app-only rollback；deploy 與 service health 分別 FAIL |
| G17 | L36 首次之後自動極小 v2 全流程 | controller/Developer/Reviewer/DevOps/root 重跑 G02–G16 + P7；時間序 v2 work 在 v1 accepted 後 | release 1.0.1、C2!=C1、D2!=D1；source_url 有實際新功能；新 Issue/PR/review/CI/deploy；scope 不變 | 不得只改 receipt、重啟 v1 或宣稱一次性腳本已滿足 |
| G18 | L40 隔離 Oracle app，不碰 Hermes | preflight 記錄 app-only host/path/port/container/network 邊界、核准 Hermes 基線；DevOps 部署後同讀-only health/uptime/id 比對 | Hermes 未 restart/replace、未改 mount/data/config/global policy；port 不衝突；rollback 演練 P8 | scope 無法證明則停；不得自行改 proxy/firewall/Hermes |
| G19 | L41 新 repo/git metadata 限定權限、不重用舊 pilot | controller/Reviewer 核對本新卡 worktree/.git 授權範圍/owner/有效期與 actual operations | 證據限定本 repo/workspace，無無界永久 grant，無舊四目錄借用 | needs_input/capability，不能自行放寬安全配置 |
| G20 | L42 最小授權、不讀 secret、socket 高風險 | 每角色核對工具/credential 使用及去敏 logs；DevOps Docker inspect mounts/security | 不讀 .env/auth/private key/token 內容，不入聊天或 app；Docker host 能力明確核准，app 無 socket | 停未授權操作；洩漏風險交 owner 處理，不自行旋轉憑證 |
| G21 | L43 新支出 0、免費額度/計費控制 | preflight 在觸發 Actions/registry 前查剩餘額度和硬控制；重跑前重新確認總預算 | 無付費 runner/新資源；可證明兩輪及有限重驗在免費配額內且不允許新增付費 | 不明即 blocked 該 gate；不得先跑再問 |
| G22 | L44 最終分項、不以缺證據稱完整成功 | root 產出功能/v1/v2/自治可見性/安全/阻礙分項，對每列 artifact 回讀 | 必需列全驗後才總 PASS；缺失列為未驗證/FAIL，報 exact C/D/CI/review/HTTP | 根不得完成；可交付已完成的獨立階段 |

## B. 產品測試協定（由 Developer 實作測試，不是本卡執行結果）

Developer 須提供可在 CI 執行的 `python -m unittest discover -s tests -v` 或 README 明確等價命令；實際命令/exit 必須放 handoff。測試 fixture 可用合成 metadata，但須標為 unit fixture，不能混進真實 release evidence。

| Case | 可執行步驟 | 斷言 |
|---|---|---|
| P1 | 啟動有效 fixture app，GET `/`、`/version`、`/healthz`，解析 HTML links/JSON；HEAD 三路徑；POST `/version`；GET 隨機與 traversal 路徑 | spec 欄位、status、Content-Type、no-store 相符；HEAD 無 body；405/Allow；404、不寫入；HTML 無未 escape 值 |
| P2 | 在獨立進程依序用缺 metadata、壞 JSON、錯 SHA、壞時間、錯 URL host/path、javascript scheme、URL credentials、缺 receipt、receipt commit mismatch、過大 receipt 啟動或請求 | 每例非零啟動或 503；絕不能 200+ok/假版本；錯誤不含秘密/stack/path |
| P3 | 已運行的有效 app 中撤下/損壞 app-only fixture receipt，再 GET health/version，恢復正確 receipt 重查 | 損壞立刻 503，恢復後 200；無沿用 cached green |
| P4 | 用 C_A metadata build image，容器啟動時傳假 C_B env；inspect build label / HTTP；做 two-build C_A/C_B fixture 比對 | runtime env 不可覆寫 baked commit；label/metadata 一致；明標本地 unit/container fixture 而非已部署 revision |
| P5 | CI 對真實 C 產生 metadata/build image，smoke 啟動、HTTP、security inspect；DevOps 對真正 Oracle container 重做 | CI/local 不是 Oracle 證據；兩者分別有實際記錄，Oracle HTTP C 和核准 digest/image mapping 全符 |
| P6 | 本地 gate 驗證輸入：舊 review SHA、錯 CI head、empty required checks、pending/failure/skipped checks、漏 readback、錯 digest | 每例 gate 拒絕；若真的 CI/review 退件，另存 request_changes/新 C 的真實重驗。不得把 control test 當真人退件 |
| P7 | v2 全 v1 regression + JSON source_url、HTML anchor；從實際 Oracle 取 source_url 再用授權 GitHub API 查該 C | exact `repository_url/commit/C2`、1.0.1、無新權限/DB；C2 真實存在且和 page/JSON 相同 |
| P8 | 已成功 app 的隔離 candidate 部署壞 receipt/不健康 image（先本地 Docker，再在明確 app-only 授權內演練），觸發 bounded timeout/rollback | candidate 不宣告成功；舊 C/D HTTP 恢復；v1 首部署無舊版則清理本 app；Hermes 不變；rollback 失敗停止並阻擋 |

### HTTP 現場核對命令範本

以下命令是未執行的操作介面，不含捏造 host/SHA。後續 worker 必須先從已核准部署及 exact-head artifacts 設定 `BASE_URL`、`EXPECTED_COMMIT`、`EXPECTED_RELEASE`、`EVIDENCE_DIR`；缺一就 fail，不猜預設目的地。`EVIDENCE_DIR` 限當前任務可寫目錄。版本/健康/頁面需同一次部署收集。

```sh
: "${BASE_URL:?approved app URL required}"
: "${EXPECTED_COMMIT:?reviewed full SHA required}"
: "${EXPECTED_RELEASE:?release required}"
: "${EVIDENCE_DIR:?authorized evidence directory required}"
curl --fail-with-body --silent --show-error --max-time 5 "$BASE_URL/healthz" -o "$EVIDENCE_DIR/health.json"
curl --fail-with-body --silent --show-error --max-time 5 "$BASE_URL/version" -o "$EVIDENCE_DIR/version.json"
curl --fail-with-body --silent --show-error --max-time 5 "$BASE_URL/" -o "$EVIDENCE_DIR/index.html"
python3 -c 'import json,os,pathlib,re; p=pathlib.Path(os.environ["EVIDENCE_DIR"]); h=json.loads((p/"health.json").read_text()); v=json.loads((p/"version.json").read_text()); assert h=={"status":"ok","checks":{"build_metadata":"ok","deployment_receipt":"ok"}}; assert re.fullmatch("[0-9a-f]{40}",v["commit"]); assert v["commit"]==os.environ["EXPECTED_COMMIT"]; assert v["release"]==os.environ["EXPECTED_RELEASE"]; assert v["schema_version"]==1; assert v["repository_url"]=="https://github.com/timmypai/agent-delivery-status"; assert v["deployment"]["id"]; print("HTTP identity assertions passed")'
```

執行 shell 須 fail-fast（例如 `set -eu`）並 export 四變數給 Python；保存每個 curl status/header、執行時間及 exit。不接受只留最後 print。上面未驗證 link 真實性/digest/獨立 review，必須再做 E1–E3。

## C. 外部 gate 的具體回讀

### E1 — repo/Issue/PR（授權後由對應角色執行）

- 建立前 `gh api repos/timmypai/agent-delivery-status`：200 表示已存在，要核對是否本專案且可安全沿用；明確 404 仍要排除 private repo 無權限造成的不可見，查 authenticated owner/repo visibility 權限，不盲建。401/403/timeout 一律不是「不存在」。建立後 read exact endpoint，解析 owner.login/name/private/full_name，private 必須 true。
- 每輪 `gh api repos/timmypai/agent-delivery-status/issues/$ISSUE_NUMBER` 和 `.../pulls/$PR_NUMBER`（number 由真實 API 結果取得，正整數），核對 repo、URL、Issue 非 PR、PR 關聯 Issue、head.sha=C；保存去敏必要欄位，不 dump tokens。
- 所有 POST/push/merge/部署等由有權角色操作後，read exact target。API 有分頁須讀完 relevant pages；解析失敗不接受。不要以 gh auth 登入當 workflow/budget/VM 授權。

### E2 — 獨立 review / required CI / image

- `gh api repos/timmypai/agent-delivery-status/commits/$C/check-runs` 與 branch rules/預先確認的 required set 對照；並讀對應 `actions/runs/$RUN_ID`。PR review 可用 GitHub review 或原生獨立 Reviewer handoff，但必須包含 reviewer profile、task/run、verdict、exact C；不能用實作者自評替代。
- CI run 讀回 repository、event、head_sha、status、conclusion、run URL；artifact/log 記 `git rev-parse HEAD`。required checks 中 `test`/`docker-smoke`（或經 scope 明確映射的實際名稱）每個都有 exact-C success，不把 pull_request merge SHA 混同 author head。
- `docker image inspect "$IMAGE_REF"`：僅擷取 `.Id`、`.RepoDigests`、`.Config.Labels["org.opencontainers.image.revision"]`，避免列印 env。與 CI build artifacts/immutable transfer 對照；不以 mutable tag 為證。
- merge 是獨立 gate；如有 merge，回讀 merged/merge_commit_sha，若部署 commit 換成 merge SHA，重跑該 SHA 全 gates。禁止把 PR merged 等同已部署。

### E3 — Oracle 實際部署及 rollback

- 先證明核准 Oracle host identity/架構/app path/port，留下 Hermes 原有 service identity/uptime/read-only health 基線（不列印秘密環境）；無明確 host 不執行 deploy。
- 只對核准 app container 做 `docker inspect`，選取 `.State.Status`、`.State.Health`（若有）、`.Image`、`.HostConfig.ReadonlyRootfs`、`.HostConfig.Privileged`、`.Config.User`、mount types/targets、ports 與資源限制；不得 dump `.Config.Env`。image ID 再與 E2 image inspect/registry manifest platform mapping 連結。
- 透過核准入口由實際外部/指定 client 執行上方 HTTP probes，保存 timestamp/status/header/body。loopback check 可補充，不能假冒使用者可達入口；無公開入口授權可採已核准私網/tunnel，但明載測點與可達範圍，不自行新開 firewall/tunnel。
- receipt C、baked C、review C、CI C、image OCI revision C、HTTP C 全同；運行 container image ID 與 D mapping 全同。收集後確認 Hermes 基線未改。
- P8 需保留舊 C/D/receipt，candidate 失敗與 rollback 命令/exit、舊版恢復 HTTP、Hermes 不變的證據。僅演練本地時明確標記，不能聲稱 Oracle rollback 已演練。

## D. 證據命名與最終 verdict

建議每卡於自己的授權 artifacts 目錄保留 `v1/`、`v2/` 子目錄（不是第二任務台帳）：去敏 repo/Issue/PR/readback、test log、review handoff locator、CI run/check readback、build metadata、image inspect/mapping、deployment receipt、HTTP、rollback、notification/UI 證據。跨 worktree 不假設內容自動整合，交接 exact path/commit/artifact checksum。

每份 release 報告需填：root/card/run、C、reviewer verdict(C)、PR/head、required check names/run/結論、D/image ID、Oracle container/HTTP/時間、舊版/rollback、預算/授權證據、v2 是否真事件接續、缺失列。N/A 只能用於真正不適用（例如本規格卡無 commit），不得用 N/A 略過必需 goal。

本卡實際可聲稱：兩份 Markdown 設計文件及 traceability 驗證；獨立 verdict **未執行**；產品測試/CI/雲端部署 **未執行**。後續 root 必須讀最新原生 task state，而非把 `native-admission.json` 當即時任務狀態。
