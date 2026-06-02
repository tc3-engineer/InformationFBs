# F_GetVersionRAIDController

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `[Obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionRAIDController.TcPOU`](../examples/P_Demo_F_GetVersionRAIDController.TcPOU) |

---

## 1. 功能简述

⚠️ **本函数已废弃**（PDF 明确：obsolete and should not be used）。请改用全局常量 `stLibVersion_Tc2_IoFunctions`。本函数与 `F_GetVersionTcIoFunctions` 功能等价，是名称不同的历史遗留。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 1 = major、2 = minor、3 = revision。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

与 `F_GetVersionTcIoFunctions` 完全相同：`nVersionElement = 1` 返回 major、`= 2` 返回 minor、`= 3` 返回 revision。函数无状态、同步返回，单个 PLC 周期完成。历史上 RAID Controller 子库可能曾经独立维护过版本号，但目前与整库版本一致，本函数仅作历史兼容。**新工程改用 `stLibVersion_Tc2_IoFunctions` 直接访问。**`nVersionElement` 取非 1/2/3 值的返回行为 PDF 未定义；建议不要依赖。

## 4. 错误码 / 返回值

本函数返回 `UINT` = 所选版本字段。

| nVersionElement | 返回值含义 |
|---|---|
| 1 | 主版本号 |
| 2 | 次版本号 |
| 3 | 修订号 |
| 其它 | 未明确定义 |

## 5. 使用注意 / 常见坑

- **已废弃**——新工程改用 `stLibVersion_Tc2_IoFunctions`。
- 功能与 `F_GetVersionTcIoFunctions` 完全相同；只是名字不同。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionRAIDController.TcPOU`](../examples/P_Demo_F_GetVersionRAIDController.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：RAID 子模块版本检查的旧代码；不推荐使用。
- **价值**：向后兼容。
- **替代方案对比**：
  - `stLibVersion_Tc2_IoFunctions`
  - `F_GetVersionTcIoFunctions`（同样已废弃）
  - **本 FC**：仅旧工程兼容

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html （⚠️ 该条目在 InfoSys 没有专属页面，URL 指向库版本页作为替代说明）
- **相关 FB / FC**：`stLibVersion_Tc2_IoFunctions`, `F_GetVersionTcIoFunctions`
