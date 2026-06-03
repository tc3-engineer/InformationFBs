# F_EcGetSyncUnitName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/14455123595.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_EcGetSyncUnitName.TcPOU`](../examples/P_Demo_F_EcGetSyncUnitName.TcPOU) |

---

## 1. 功能简述

通过 Sync Unit 的 Object ID 读取该 SU 的名称字符串。返回 `HRESULT`。是 SU 诊断中"OID → 人类可读名"的最后一步。

## 2. 接口定义

**FUNCTION 声明（PDF §4.24 原文逐字）**：

> `METHOD F_EcGetSyncUnitName : HRESULT`（PDF 标 METHOD，实际 FUNCTION）
>
> Inputs:
> - `oidSyncUnit : OTCID;` (object ID of sync unit)
>
> Outputs:
> - `sSyncUnitName : STRING(63);`

### VAR_INPUT 参数

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `oidSyncUnit` | `OTCID` | — | 要查询的 Sync Unit Object ID |

### VAR_OUTPUT 参数

| 名称 | 类型 | 说明 |
|---|---|---|
| `sSyncUnitName` | `STRING(63)` | SU 名称（最长 63 字符） |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即返回**：同步 FUNCTION，无 `bExecute`，立即返回。

**用途**：诊断输出报告时把 OID 变人话 —— HMI 显示"当前出错的是 'SU_Motion'"比"OID=12345"友好得多。配合 `F_EcGetLinkedTaskOfSyncUnit` 可输出完整的"SU 名 + Task 名"对照表，是 SCADA 集成与远程诊断的关键 FC 之一。SU 名通常在 XAE 工程中由工程师手工命名（如 SU_Motion、SU_Process 等），代表业务分组语义。

**返回值**：
- `SUCCEEDED(hr) = TRUE`：成功
- 失败：HRESULT 错误码

**典型陷阱**：
- TwinCAT 版本要求：v3.1.4024.48 + Tc2_EtherCAT ≥ 3.4.2.0
- `sSyncUnitName` 上限 63 字符，工程命名应控制长度
- `oidSyncUnit = 0` 必失败 —— 先用 XAE 主站 Process Image 视图查每个 SU 的 OTCID

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `S_OK` (0) | 成功 | 读 sSyncUnitName |
| `E_FAIL` | 失败 | 检查 oidSyncUnit |

## 5. 使用注意 / 常见坑

- **配合诊断脚本**（工程经验补充）：HMI / 日志输出报告用
- **`STRING(63)` 容量**：超长会截断
- **`SUCCEEDED` 习惯**：判 HRESULT 用专用宏

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_EcGetSyncUnitName.TcPOU`](../examples/P_Demo_F_EcGetSyncUnitName.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 诊断页面要显示"当前网络中包含 SU 列表"。给操作员看 OID 数字毫无意义；本 FC 帮把 OID 变成 SU 名字
- **价值**：把内部 ID 转化为业务可读
- **替代方案对比**：硬编码"OID 1 = SU_Motion" → 工程变更失同步；本 FC → 永远跟工程同步

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.24
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/14455123595.html
- **相关 FB / FC**：`F_EcGetLinkedTaskOfSyncUnit`、`FB_EcGetAllSyncUnitSlaveAddr`
