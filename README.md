# tc3-libraries-kb

由 **Claude Code（云端）** 维护的 TwinCAT 3 全库知识库。覆盖 ~40 个 Beckhoff PLC 库 / ~1500-2000 个 FB+FC，所有文档以官方 PDF 为唯一可信源，每篇生成时**自动二次校验**。**每篇文档配套一个 TcPOU 例程文件，可直接导入 TwinCAT 3 XAE 运行验证**。

## 工作方式：单 session + slash commands

不用 routines、不用 cron、不用脚本。在 [claude.ai/code](https://claude.ai/code) 打开本仓库后直接对话：

```
/discover Tc2_System              # 抓 PDF、解析目录、生成 roadmap
/doc-shard Tc2_System ADS         # 生成 ADS 类一批文档（含自验证）
/verify Tc2_System/ads/ADSREAD.md # 抽检某篇
/next                             # 看进度并推荐下一步
```

每条命令完整跑完一个闭环（含 PR），中间可随时打断/纠正。

## 质量保证：每篇 self-verify

`/doc-shard` 生成每篇文档后会**第二次独立抓取 PDF**，与刚写的文档逐字段对照（VAR 名、类型、注释、关键事实），写入 `_meta/verify/<library>/<name>.md`。

- ✅ PASS → 文档头 Status = `verified`
- ❌ FAIL → 自动修正后再 verify 一次；连续两次失败标 `⚠️ verify-failed` 并记入 `_meta/blocked.md`

PR 描述里会列出每篇的 verify 结果，你 review 时优先看 verify-failed 的。

## 例程：TcPOU 原生格式，拖拽即用

每个 FB/FC 配套一个 `.TcPOU` 文件（TwinCAT 3 原生 XML / TcPlcObject schema），含一个 PROGRAM POU 演示该 FB 用法。

**导入步骤（TwinCAT 3 XAE）**：
1. 右键 PLC 项目（`<MyProject> Project` 节点）
2. 选 **Add → Existing Item...**
3. 选 .TcPOU 文件 → OK
4. POU 出现在树中
5. 把 POU 加到 PlcTask（或在 MAIN 里调一下）→ 编译 → 登录 → 在线监视输出

每个 .TcPOU 顶部有中文验证步骤注释，明确告诉你"强制 X，观察 Y"。

> **为什么改成 `.TcPOU` 而不是之前的 PLCopenXML（`.xml`）**：原版 PLCopenXML 例程需要 XAE 走 **Import PLCopenXML** 向导，且 Beckhoff 官方原话指出「PLCopenXML defines a subset of the elements known in TwinCAT. 100% compatibility is therefore not ensured.」`.TcPOU` 是 TwinCAT 3 原生 schema（`TcPlcObject`），**直接拖入 PLC `POUs` 文件夹即可使用**，保留 `SpecialFunc`、稳定 GUID 等元数据，免去子集映射。代价：`.TcPOU` 是 Beckhoff 私有格式，不能跨导入到 CODESYS / TIA / B&R 等非 Beckhoff IDE — 本仓库定位是 TwinCAT 3 文档与例程，原生格式优先。

## 目录结构

```
tc3-libraries-kb/
├── CLAUDE.md                          ← Claude Code 自动加载的项目级指令
├── README.md                          ← 本文件
├── .claude/
│   └── commands/                      ← 4 个 slash commands
│       ├── discover.md                /discover <library>
│       ├── doc-shard.md               /doc-shard <library> <category>
│       ├── verify.md                  /verify <path>
│       └── next.md                    /next
├── _templates/
│   └── fb-template.md                 文档强约束模板
├── _meta/
│   ├── library-catalog.md             40 库总目录与状态
│   ├── roadmap-<library>.md           每库一份清单（discover 自动生成）
│   ├── progress.md                    每篇文档的状态日志
│   ├── verify/<library>/<name>.md     每篇的 verify 报告
│   └── blocked.md                     verify-failed 集合
└── <Library>/                         每库一个目录
    ├── README.md                      库索引（discover 生成，doc-shard 更新）
    └── <category>/<Name>.md           按 PDF 章节分类
```

## 一次性配置

1. 上传仓库到 GitHub
2. 在 [claude.ai/code](https://claude.ai/code) 建一个 web session，关联本仓库
3. **环境网络配置**（重要）：
   - 默认 Trusted 即可；如果发现 PDF 抓取被 block，把环境改 Custom 并加：
     - `infosys.beckhoff.com`
     - `download.beckhoff.com`
4. 第一次开 session 时，Claude Code 会自动加载 `CLAUDE.md`，可以直接打 `/next` 看下一步

## 推进路径（已为 Tier 1 配好基础）

```
当前: Tc2_Standard 3/31 verified（手工金样本 RS / SR / TON）
↓
/doc-shard Tc2_Standard Counter         # 3 条
/doc-shard Tc2_Standard Timer           # 2 条剩余（TON 已 done）
/doc-shard Tc2_Standard Trigger         # 2 条
/doc-shard Tc2_Standard String functions               # 9 条
/doc-shard Tc2_Standard String functions (WSTRING)     # 9 条
/doc-shard Tc2_Standard Timer (LTIME)   # 3 条
/doc-shard Tc2_Standard Bistable        # 0 条剩余（RS/SR 已 done）

# Tc2_Standard 收尾后 → Tier 1 推进
/discover Tc2_System
/doc-shard Tc2_System General
/doc-shard Tc2_System ADS
... (每个 category 一条命令)

/discover Tc2_Math
/discover Tc2_Utilities
/discover Tc3_EventLogger
... (类似)
```

完整 40 库见 `_meta/library-catalog.md`，按 5 层优先级。

## Review 流程

每条 `/doc-shard` 自动开 PR 到 `claude/doc-<lib>-<category>-<时间戳>` 分支。Review 时：

1. 看 PR body 的 verify 结果表，重点看 ⚠️ 的
2. 抽 1-2 篇用 `/verify <path>` 三次确认
3. 没问题 squash merge
4. 有问题在 PR 里 comment，下次 session 用 `/doc-shard` 加 hint 重跑该批

## 数据流

```
官方 PDF ──fetch──▶ Claude Code session
                        │
                        ├─ /discover  → roadmap + 库 README
                        │
                        ├─ /doc-shard → 文档 .md
                        │      │
                        │      └─ self-verify (第二次 fetch)
                        │             │
                        │             ├─ ✅ → Status: verified
                        │             └─ ❌ → 自动修正 / blocked.md
                        │
                        ├─ /verify  → 临时抽检报告（chat only）
                        │
                        └─ /next    → 进度仪表盘
```
