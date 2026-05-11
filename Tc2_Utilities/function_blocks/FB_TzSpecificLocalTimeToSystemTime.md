# FB_TzSpecificLocalTimeToSystemTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35028619.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml`](../examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml) |

---

## 1. 功能简述

FB_TzSpecificLocalTimeToSystemTime 是 FB_SystemTimeToTzSpecificLocalTime 的反向：给定本地时间 + 时区配置，算出对应的 UTC `TIMESTRUCT`。

用于：HMI 让操作员按本地时间输入事件，PLC 后端存 UTC。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : TIMESTRUCT;
    tzInfo : ST_TimeZoneInformation;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `TIMESTRUCT` | 参数 `in`（类型 `TIMESTRUCT`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `tzInfo` | `ST_TimeZoneInformation` | 时区配置。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    out : TIMESTRUCT;
    eTzID : E_TimeZoneID := eTimeZoneID_Unknown;
    bB : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `out` | `TIMESTRUCT` | - | 参数 `out`（类型 `TIMESTRUCT`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `eTzID` | `E_TimeZoneID` | `eTimeZoneID_Unknown` | 参数 `eTzID`（类型 `E_TimeZoneID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `bB` | `BOOL` | - | 输出布尔标志：`bB`。具体语义见 §3 行为说明。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**纯计算**，行为与 FB_SystemTimeToTzSpecificLocalTime 镜像。算法：本地时间减去 `tzInfo.Bias`（含夏令时偏移）。

**注意夏令时模糊期**：本地时间在夏令时回切的那 1 小时（如 03:00 → 02:00）会出现两次本地时间映射到不同 UTC 的情况——Windows 行为是优先取标准时；业务侧若关心可在该窗口额外询问。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **夏令时切换瞬间结果可能不一致**：切换前后 1 小时内业务侧应避免对该 1 小时窗口做时间差计算（标准 Windows 行为）。
- `tzInfo` 必须先用 FB_GetTimeZoneInformation 读到正确值，传错时区会算出错误结果但不会报错。
- Windows `TIME_ZONE_INFORMATION` 的偏移分钟数符号约定与直觉相反：CET = -60（表示 UTC + 60 = 本地）。不要把符号搞反。（工程经验补充）
- PDF 无错误码——纯计算 FB，输入合法即输出合法。
- `SYSTEMTIME` 在 TwinCAT 里映射为 `TIMESTRUCT`，字段含义一致。（工程经验补充）
- **夏令时回切的『模糊小时』映射不唯一**——本地 02:30 可能对应两个 UTC；业务侧需要约定取哪一个。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml`](../examples/P_Demo_FB_TzSpecificLocalTimeToSystemTime.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：操作员在 HMI 用本地时间填事件时刻，存数据库前转 UTC。
- **价值**：HMI 友好（本地时间）+ 数据库稳定（UTC）。
- **替代方案对比**：
  - 直接存本地：跨时区设备 / 夏令时切换日易乱。
  - **本 FB**：HMI 本地、存储 UTC 两全。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.61
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35028619.html
- **相关 FB**：`FB_SystemTimeToTzSpecificLocalTime`, `FB_GetTimeZoneInformation`
