# SYSTEMTIME_TO_TOD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16285494795.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SYSTEMTIME_TO_TOD.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_TOD.TcPOU) |

---

## 1. 功能简述

从 `TIMESTRUCT` 提取「一天内时间」（`TOD`，毫秒精度）。返回 0 = 错误，> 0 = 该天 00:00:00 起的 `TOD` 值。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION SYSTEMTIME_TO_TOD : TOD
VAR_INPUT
    systemTime : TIMESTRUCT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `systemTime` | `TIMESTRUCT` | 待转换的 Windows 系统时间结构体 |

### 返回值

`TOD` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

函数按 `TIMESTRUCT.wHour * 3600000 + wMinute * 60000 + wSecond * 1000 + wMilliseconds` 计算 `TOD`（毫秒数）。

`TOD` 范围 0 ~ 86399999（00:00:00.000 ~ 23:59:59.999）。

返回 0 表示错误（输入字段越界）或合法的 00:00:00.000——PDF 把 0 标为「错误」，但严格说 00:00:00.000 = 0 也是合法值，**调用方应先校验输入字段合法性**。

版本要求：TwinCAT v3.1.4024.0 + Tc2_Utilities ≥ 3.7.3.0。


本 FC 在「按时刻触发」类业务中频繁出现：每天 8 点准时启动设备、每天 22 点关闭照明、每天 0 点重置日产量计数。把 `TIMESTRUCT` 转成 `TOD` 后用 `>=` 比较一个常量阈值是最直观的写法。注意要么提前过滤掉无效输入要么接受 0 作为合法值。

## 4. 错误码 / 返回值

返回类型 `TOD`。函数语义详见 §3。某些 FC（返回 `WORD` / `T_FILETIME64` / `TOD` 的）以 0 作为「参数错误」哨兵值——调用方必须先检查 > 0；具体见 §5 使用注意。

## 5. 使用注意 / 常见坑

- **0 返回值有歧义**：00:00:00.000 也是 0，PDF 把它列为「错误」——先确认输入合法再相信结果。
- **忽略日期 / 年 / 月 / 日字段**：本 FC 只用时分秒毫秒，把「2099-12-31 23:59:59.999」转得到的 TOD 与「2026-05-11 23:59:59.999」相同。
- **精度毫秒**：与 `TIMESTRUCT.wMilliseconds` 一致；纳秒级精度需要 `FILETIME64_TO_TOD`（但本质也是毫秒精度因为 TOD 只到 ms）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SYSTEMTIME_TO_TOD.TcPOU`](../examples/P_Demo_SYSTEMTIME_TO_TOD.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
timeOfDay := SYSTEMTIME_TO_TOD(systemTime);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：按时间段触发的业务逻辑：每天 8 点上班启动设备 / 每天 22 点关灯——只需要时刻不需要日期。
- **价值**：1 行调用完成时分秒到 `TOD` 类型的折算，避免手写权重相乘相加。
- **替代方案对比**：手写权重计算（容易写错）/ 走 `SYSTEMTIME_TO_FILETIME64` + `FILETIME64_TO_TOD`（多 1 步）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.22
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/16285494795.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
