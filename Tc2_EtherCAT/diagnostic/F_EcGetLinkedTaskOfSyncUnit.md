# F_EcGetLinkedTaskOfSyncUnit

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11328546443.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_EcGetLinkedTaskOfSyncUnit.TcPOU`](../examples/P_Demo_F_EcGetLinkedTaskOfSyncUnit.TcPOU) |

---

## 1. 功能简述

通过 Sync Unit 的 Object ID 读取关联到该 Sync Unit 的 task 名称与 Object ID。返回 `HRESULT` 指示调用是否成功。

## 2. 接口定义

**FUNCTION 声明（PDF §4.23 原文逐字）**：

> `METHOD F_EcGetLinkedTaskOfSyncUnit : HRESULT`（PDF 标 METHOD，实际是 FUNCTION）
>
> Inputs:
> - `oidSyncUnit : OTCID;` (object ID of sync unit)
>
> Outputs:
> - `sLinkedTask   : STRING;`
> - `oidLinkedTask : OTCID;` (object ID of linked task)

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `oidSyncUnit` | `OTCID` | — | 要查询的 Sync Unit Object ID（可在 XAE 主站 Process Image 中找到） |

### VAR_OUTPUT 参数

| 名称 | 类型 | 说明 |
|---|---|---|
| `sLinkedTask` | `STRING` | 关联 task 的名称 |
| `oidLinkedTask` | `OTCID` | 关联 task 的 Object ID |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION，无 `bExecute`，直接返回 HRESULT。

**Sync Unit 与 Task 的关系**：TwinCAT 3 每个 Sync Unit 必须挂载到一个 task，task 周期决定 SU 的循环频率。本 FC 把"我有这个 SU OID"翻译成"这个 SU 被哪个 task 驱动"。配合 `F_EcGetSyncUnitName`、`FB_EcGetAllSyncUnitSlaveAddr` 可以组成一条完整查询链：先列出全部 SU、查每个 SU 挂哪个 task、查每个 SU 包含哪些从站，从而把整张"task → SU → 从站"的拓扑表自动重建出来。

**典型用法**：
- 工程分析：列出"哪些 SU 挂在 1 kHz task、哪些挂在 100 Hz task"
- 诊断：怀疑某 SU 超时时确认它绑的 task 周期
- 自动生成"工程结构文档"的工具链中作为节点查询函数

**返回值（`HRESULT`）**：
- `SUCCEEDED(hr) = TRUE`：读取成功
- 失败：错误码在 HRESULT 中，对照 Windows HRESULT 表

**典型陷阱**：
- TwinCAT 版本要求 v3.1.4024.22 + Tc2_EtherCAT ≥ 3.3.17.0
- `oidSyncUnit = 0` 必失败；先用 `F_EcGetSyncUnitName` 或 XAE 查 SU 列表

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `S_OK` (0) | 成功 | 读 sLinkedTask / oidLinkedTask |
| `E_FAIL` 等 | 失败 | 检查 oidSyncUnit 是否有效 |

## 5. 使用注意 / 常见坑

- **`SUCCEEDED(hr)` 习惯**：判 HRESULT 时用 `IF SUCCEEDED(F_EcGetLinkedTaskOfSyncUnit(...))` 而非 `= 0`
- **`STRING` 默认 80 字符**：task 名超过 79 字符会被截断（极少发生）
- **作为工程分析工具**（工程经验补充）：写"工程结构自动文档化"脚本时用

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_EcGetLinkedTaskOfSyncUnit.TcPOU`](../examples/P_Demo_F_EcGetLinkedTaskOfSyncUnit.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工程师接手陌生工程，需要了解"哪个 SU 挂哪个 task"；本 FC 作为脚本自动遍历输出报告，免去逐个右键 SU 查 properties
- **价值**：把工程拓扑结构变可程序化访问
- **替代方案对比**：XAE 手工查 → 慢；本 FC → 一行调用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.23
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/11328546443.html
- **相关 FB / FC**：`F_EcGetSyncUnitName`、`FB_EcGetAllSyncUnitSlaveAddr`
