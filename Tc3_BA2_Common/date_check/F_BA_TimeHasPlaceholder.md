# F_BA_TimeHasPlaceholder

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Types / Date and Time / Check` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785377931.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_TimeHasPlaceholder.TcPOU`](../examples/P_Demo_F_BA_TimeHasPlaceholder.TcPOU) |

---

## 1. 功能简述

检测 `ST_BA_Time` 中的 hour / minute / second 是否包含占位符（`16#FF`）。返回 BOOL。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_TimeHasPlaceholder : BOOL
VAR_INPUT
  stTime    : ST_BA_Time;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stTime` | `ST_BA_Time` | - | 被检查的 BA 时间结构。 |

### VAR_IN_OUT

无。


## 3. 行为说明

检测 `ST_BA_Time` 中的 hour / minute / second 是否包含占位符（`16#FF`）。返回 BOOL。 接入参数：`stTime`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 本 FC 不处理时区——所有日期 / 时间均假定为本地时间；若工程需要 UTC，请在上层完成偏移换算。 典型工程场景：调度条目的时间字段："每天 10:30:?? 触发"（秒未指定）。

## 4. 错误码 / 返回值

本 FC 返回类型为 `BOOL`。

本 FC 返回 BOOL：`TRUE` = 判定成功 / 条件满足；`FALSE` = 判定失败 / 条件不满足。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。
- 日期 / 时间相关 FC 不会处理时区——所有时间均假定本地时间。需要 UTC 时上层自己换算。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_TimeHasPlaceholder.TcPOU`](../examples/P_Demo_F_BA_TimeHasPlaceholder.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：调度条目的时间字段："每天 10:30:?? 触发"（秒未指定）。
- **价值**：一行 FC 替代字段级判定。
- **替代方案对比**：逐字段 IF 比较（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.3.3.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785377931.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
