# F_Byte_to_Temp

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION` |
| Category | `Functions / byte to REAL` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173294731.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_Byte_to_Temp.TcPOU`](../examples/P_Demo_F_Byte_to_Temp.TcPOU) |

---

## 1. 功能简述

**EnOcean 温度字节线性转换函数**，返回 `REAL`。EnOcean 温度传感器（如 STM 系列、PTM 自带温度的房间面板等）把温度编码成 1 字节 0..255，对应一个厂家定义的温度量程（典型 0..40 °C，也可能是 -20..40 °C 或 0..80 °C 等）。本函数把"原始字节 + 量程下限 + 量程上限"线性映射回 °C 实数：`(byData / 255) * (maxTemp - minTemp) + minTemp`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    byData  : BYTE;
    minTemp : REAL := 0;
    maxTemp : REAL := 40;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `byData` | `BYTE` | — | EnOcean 温度字节原始值（0..255） |
| `minTemp` | `REAL` | `0` | 量程下限（°C）。`byData = 0` 时对应的温度 |
| `maxTemp` | `REAL` | `40` | 量程上限（°C）。`byData = 255` 时对应的温度 |

### VAR_OUTPUT

返回值：`REAL` —— 解码后的温度（°C）。

### VAR_IN_OUT

无。

## 3. 行为说明

**计算公式**：`Temperature = byData / 255 * (maxTemp - minTemp) + minTemp`。函数在内部把 `byData` 转 REAL，除以 255.0 得到归一化值 0.0..1.0，再乘以量程跨度并加偏移，最终返回 REAL °C。整个函数是纯计算，无内部状态，每次调用立即返回，无 `bExecute` 也无 `bBusy`，可在 PLC 周期任何位置反复调用。

**典型量程对照**：房间温控 STM100 用默认的 0..40 °C 区间；工业过程温度 sensor 常用 0..80 °C 或 -20..60 °C；户外气温 sensor 用 -40..60 °C 覆盖全季节。同一台 PLC 程序里可能要同时解码几种 sensor，各调用时填不同的 `minTemp / maxTemp` 参数即可——本函数完全无副作用，并发调用安全。

**边界值**：`byData = 0` → `minTemp`；`byData = 255` → `maxTemp`。中间值线性插值。

**精度**：`byData` 8 bit → 256 个等级。40 °C 量程下分辨率约 0.156 °C，对一般暖通空调够用；80 °C 量程下约 0.31 °C，仍能满足工业过程监控。要更高精度的温度（如计量级 0.01 °C）就要换 EnOcean 16-bit 温度 profile，不在本函数范围。

**反相编码工艺**：部分厂家把"高字节 = 低温"反着编。这种情况下传 `minTemp = 40, maxTemp = 0`（颠倒）即可——函数本身不需要知道反相，公式自然处理。

**典型陷阱**：① `byData = 255` 在某些设备里是"断线哨兵"，本函数仍按公式算出 `maxTemp`，调用方须先识别 `byData = 16#FF` 或上游 FB 的 watchdog 标志再决定要不要用这个温度。② 量程下限 / 上限填错（与设备手册不符）→ 输出温度系统性偏离真实值若干度，工程现场常见踩坑。③ `byData` 是 0..255 不是 0..100，初学常常把"百分比量程"和"0..255 编码"混淆。

## 4. 错误码 / 返回值

返回值类型 `REAL`，无错误码。极端输入：

| 输入 | 返回 |
|---|---|
| `byData = 0` | `minTemp` |
| `byData = 255` | `maxTemp` |
| `byData = 127` | `(minTemp + maxTemp) / 2` 附近（127/255 ≈ 0.498，所以略偏 minTemp 端） |
| `minTemp > maxTemp` | 反相，仍返回有效 REAL（用于反相编码场景） |

## 5. 使用注意 / 常见坑

- **必须按设备手册填量程**：默认 0..40 °C 适合房间温控；工业 / 户外要改。
- **断线哨兵识别**：用本函数之前先判 `byData = 16#FF`（部分设备）或上游 FB 的 watchdog 标志。
- **配合 `FB_EnOceanSTM100Generic`**：典型用法 `rTemp := F_Byte_to_Temp(byData := fbSTM.nDataBytes[0], minTemp := 0, maxTemp := 40);`
- **配合 `FB_Rec_Generic` 解码 ORG 7**：`rTemp := F_Byte_to_Temp(byData := fbRec.ar_Value[0], minTemp := 0, maxTemp := 40);`
- **不要在循环中重复调用同一字节**：函数是纯计算，开销小但仍建议缓存结果。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_Byte_to_Temp.TcPOU`](../examples/P_Demo_F_Byte_to_Temp.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_F_Byte_to_Temp
VAR
    byRaw  : BYTE := 153;     // 表示约 24 °C（153/255 * 40 ≈ 24）
    rTemp  : REAL;
END_VAR
rTemp := F_Byte_to_Temp(byData := byRaw, minTemp := 0, maxTemp := 40);
```

## 7. 业务场景与实际价值

- **场景**：EnOcean 温度数据自带是 1-byte 编码，PLC 应用要拿 REAL 温度做 PID 控制 / 数据归档 / HMI 显示。本函数是"原始字节 → 工程量"的最后一步。
- **价值**：免去自己写 3 行线性变换。配合 STM 系列接收 FB 直接给最终温度值。
- **替代方案对比**：
  - 自己写 `rTemp := BYTE_TO_REAL(byData) / 255.0 * (maxTemp - minTemp) + minTemp;`：3 行代码，可以但容易写错除数（用 256 而不是 255）
  - **本函数**：内置且经厂家测试，避免精度错误

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173294731.html
- **相关**：`F_Byte_to_TurnSwitch`（同节配套函数，byte → 旋钮档位）、`FB_EnOceanSTM100Generic`（典型上游使用者）、`FB_Rec_Generic`（KL6581 体系用例）
