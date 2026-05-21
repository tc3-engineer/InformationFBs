# F_GetVersionTcSystem

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `[Obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31051659.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_F_GetVersionTcSystem.xml`](../examples/P_Demo_F_GetVersionTcSystem.xml) |

---

## 1. 功能简述

**⚠️ 已废弃**：F_GetVersionTcSystem 读取 PLC 库版本信息的某个元素（major / minor / revision），每次调用只能返回一个分量。PDF 与 InfoSys 都明确建议**改用全局常量 `stLibVersion_Tc2_System`**——一次性拿到完整版本结构，无需多次调用，更安全可读。保留本函数仅为兼容老代码；新工程禁用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 要读的版本字段：1 = major、2 = minor、3 = revision。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃，不建议在新代码中使用。**

**原始行为**：根据 `nVersionElement` 取版本结构里的一个字段：

- `1` = major（主版本号）
- `2` = minor（次版本号）
- `3` = revision（修订号）

**返回值 `UINT`**：对应字段值；越界 `nVersionElement` 行为未明确，建议不要传 1-3 之外的值。

**替代方案**：直接读 `stLibVersion_Tc2_System.iMajor` / `.iMinor` / `.iBuild` / `.iRevision` 字段，一次性获取所有信息，避免 3 次函数调用。本函数在新工程中应当完全避免使用。

## 4. 错误码 / 返回值

本函数返回 `UINT`：对应字段的数值。无 build 字段访问能力。

## 5. 使用注意 / 常见坑

- **已废弃**：PDF / InfoSys 明确建议改用 `stLibVersion_Tc2_System` 全局常量。新工程不要用本函数。
- **只返回 3 个字段**：原始版本结构是 4 字段（major/minor/build/revision），本函数没有访问 build 的方式。
- **多次调用**：要拿完整版本必须调 3 次；用常量结构一行搞定。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcSystem.xml`](../examples/P_Demo_F_GetVersionTcSystem.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：**仅老代码维护场景**：维护一份多年前写的工程，看见用了 `F_GetVersionTcSystem` 时知道它在干什么。新工程一律改用 `stLibVersion_Tc2_System.iMajor` 等。
- **价值**：无新价值；已被全局常量取代。
- **替代方案对比**：
  - `stLibVersion_Tc2_System.iMajor / iMinor / iBuild / iRevision`：**推荐**，一次读所有字段。
  - `F_CmpLibVersion`：直接比对版本，省去手算。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31051659.html
- **相关 FB / FC**：`stLibVersion_Tc2_System`, `F_CmpLibVersion`
