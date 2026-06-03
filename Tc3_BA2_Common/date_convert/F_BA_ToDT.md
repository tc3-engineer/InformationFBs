# F_BA_ToDT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Types / Date and Time / Convert` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785416971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_ToDT.TcPOU`](../examples/P_Demo_F_BA_ToDT.TcPOU) |

---

## 1. 功能简述

把 `ST_BA_DateTime` 转为 IEC 标准 `DT`（DATE_AND_TIME，等价 ULINT 秒数）。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_ToDATE : DATE
VAR_INPUT
  stDate    : ST_BA_Date;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDate` | `ST_BA_Date` | - | Date input value to be converted. |

### VAR_IN_OUT

无。


## 3. 行为说明

把 `ST_BA_DateTime` 转为 IEC 标准 `DT`（DATE_AND_TIME，等价 ULINT 秒数）。 接入参数：`stDate`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景：把 BA 内部日期时间转成 IEC 标准的 DT 类型给其它库用。

## 4. 错误码 / 返回值

本 FC 返回类型为 `DATE`。

本 FC 返回 `DATE` 类型：表示对应的时间 / 日期 / 时间戳值。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_ToDT.TcPOU`](../examples/P_Demo_F_BA_ToDT.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把 BA 内部日期时间转成 IEC 标准的 DT 类型给其它库用。
- **价值**：统一类型互操作。
- **替代方案对比**：`DT_OF_DATE_AND_TOD(date, tod)` 类拼装（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.3.3.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785416971.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
