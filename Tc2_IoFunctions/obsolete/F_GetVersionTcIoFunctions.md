# F_GetVersionTcIoFunctions

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
| Example | [`examples/P_Demo_F_GetVersionTcIoFunctions.TcPOU`](../examples/P_Demo_F_GetVersionTcIoFunctions.TcPOU) |

---

## 1. 功能简述

⚠️ **本函数已废弃**（PDF 明确：obsolete and should not be used）。请改用全局常量 `stLibVersion_Tc2_IoFunctions` 读取库版本。本函数仅为旧工程兼容保留。

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

`nVersionElement` 选择要读的版本字段：1 = major（主版本）、2 = minor（次版本）、3 = revision（修订）。函数返回该字段值（UINT），通过简单查找内部表实现，无状态、同步返回，单个 PLC 周期完成。**新工程应改用 `stLibVersion_Tc2_IoFunctions.iMajor` / `.iMinor` / `.iBuild` 直接读全局常量**——不需要函数调用，编译期解析无运行时开销。维持本函数仅为不修改旧工程的兼容性考虑；新工程不要用。`nVersionElement` 取非 1/2/3 值的返回行为 PDF 未明确定义，建议不要依赖。

## 4. 错误码 / 返回值

本函数返回 `UINT` = 所选版本字段。

| nVersionElement | 返回值含义 |
|---|---|
| 1 | 主版本号 (major) |
| 2 | 次版本号 (minor) |
| 3 | 修订号 (revision) |
| 其它 | 实现定义（PDF 未说明） |

## 5. 使用注意 / 常见坑

- **本函数已废弃**——新工程不要用。改用全局常量 `stLibVersion_Tc2_IoFunctions`。
- PDF 与 InfoSys 未列对应错误码；非 1/2/3 值的返回行为未明确定义。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcIoFunctions.TcPOU`](../examples/P_Demo_F_GetVersionTcIoFunctions.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：旧工程升级 TwinCAT 3 时，原代码若调用本函数仍可工作但建议改写。
- **价值**：向后兼容旧工程；新工程不要用。
- **替代方案对比**：
  - **`stLibVersion_Tc2_IoFunctions`** 全局常量：标准做法
  - 本 FC：仅旧工程兼容

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59267851.html （⚠️ 该条目在 InfoSys 没有专属页面，URL 指向库版本页作为替代说明）
- **相关 FB / FC**：`stLibVersion_Tc2_IoFunctions`, `F_GetVersionRAIDController`
