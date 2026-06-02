# GETSYSTEMTIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `[Obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30960907.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_GETSYSTEMTIME.TcPOU`](../examples/P_Demo_GETSYSTEMTIME.TcPOU) |

---

## 1. 功能简述

**⚠️ 已废弃**：GETSYSTEMTIME 是功能块，读取系统时间戳（64 位整数，每单位 100ns，1601-01-01 以来的累计计数）。PDF 明确指出**改用 `F_GetSystemTime` 函数**——只需一个返回值而不是两个输出，调用更简洁。保留本 FB 仅为兼容老代码。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    timeLoDW : UDINT;
    timeHiDW : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `timeLoDW` | `UDINT` | **输出**：时间戳低 32 位。 |
| `timeHiDW` | `UDINT` | **输出**：时间戳高 32 位。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**已废弃，不建议在新代码中使用。**

**原始行为**：每次调用都更新 64 位时间戳，拆成 `timeLoDW`（低 32 位）和 `timeHiDW`（高 32 位）两个 `UDINT` 输出。

**时间起点**：1601-01-01 00:00:00 UTC，与 Windows FILETIME 一致。

**单位**：100 ns。要换算成秒需 `/ 10_000_000`。

**替代方案**：`F_GetSystemTime()` 函数直接返回 `T_FILETIME64` 结构（含 64 位整数字段），无需手动拼装高低 32 位。

**为何废弃**：FB 形式调用啰嗦（要先实例化），返回两个分量需手动拼成 64 位。函数版本一行调用更优。

## 4. 错误码 / 返回值

本函数无错误码 / 无返回值，状态由输出参数自行反映。

## 5. 使用注意 / 常见坑

- **已废弃**：用 `F_GetSystemTime()` 函数替代。
- **手拼高低 32 位**：要得到完整 64 位需 `nFull := SHL(TO_ULINT(timeHiDW), 32) OR TO_ULINT(timeLoDW)`，易写错。
- **FB 实例化开销**：函数版本无需实例化，更省内存。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETSYSTEMTIME.TcPOU`](../examples/P_Demo_GETSYSTEMTIME.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：**仅老代码维护场景**：维护用了 GETSYSTEMTIME 的工程时知道含义。新工程一律改 `F_GetSystemTime()` 函数。
- **价值**：无新价值；已被函数版本取代。
- **替代方案对比**：
  - `F_GetSystemTime()`：**推荐**，一行调用，返回完整 64 位结构。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.7.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30960907.html
- **相关 FB / FC**：`GETTASKTIME`
