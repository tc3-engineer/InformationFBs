# F_Byte_to_TurnSwitch

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION` |
| Category | `Functions / byte to rotary switch` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173296267.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_Byte_to_TurnSwitch.TcPOU`](../examples/P_Demo_F_Byte_to_TurnSwitch.TcPOU) |

---

## 1. 功能简述

**EnOcean 旋钮位置字节转数据结构函数**。返回 `STREnOceanTurnSwitch` 结构（含 5 个互斥布尔位）。把房间控制单元面板上 5 档旋钮（Auto / 0 / 1 / 2 / 3）的 1-byte 编码翻译成五个独立布尔位 `bStageAuto / bStage_0 / bStage_1 / bStage_2 / bStage_3`，应用层用 `IF` 或 `CASE` 就能写场景脚本。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    byData  : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `byData` | `BYTE` | — | EnOcean 旋钮位置原始字节 |

### VAR_OUTPUT

返回值：`STREnOceanTurnSwitch`（含 `bStageAuto / bStage_0 / bStage_1 / bStage_2 / bStage_3`，同一时刻只有一位为 TRUE）

### VAR_IN_OUT

无。

## 3. 行为说明

**编码映射**（按 PDF 描述）：5 档旋钮在 EnOcean 协议里用 1 字节表达，本函数内部解码后返回结构体，5 位互斥代表当前档位。具体字节 → 档位的精确映射由本函数内置实现，应用层不需要知道每个 raw 字节值对应哪一档。

**返回结构 `STREnOceanTurnSwitch`** 字段：
- `bStageAuto` —— Auto 档（最右）
- `bStage_0` —— 档位 0（最左 / Off）
- `bStage_1` —— 档位 1（节能）
- `bStage_2` —— 档位 2（舒适）
- `bStage_3` —— 档位 3（Boost / 最右）

**互斥**：5 位中同一时刻只有一位 TRUE；不应出现两位同时 TRUE 的情况（旋钮物理上只能停在一个位置）。如果出现可能是字节损坏。

**典型用法**：`stTurn := F_Byte_to_TurnSwitch(byData := fbSTM.nDataBytes[2]); IF stTurn.bStageAuto THEN ... ELSIF stTurn.bStage_3 THEN ... END_IF;`

**与 `E_EnOceanRotarySwitch` 的差异**：`E_EnOceanRotarySwitch` 是枚举，5 个可能值之一（PDF §4.2.1.1.2）；本函数返回的结构体是 5 个布尔位。二者表达同一信息，使用方式不同——枚举用 CASE 写 switch 分支，结构体用并列 IF 写。`FB_EnOceanSTM100` 输出枚举；本函数适合自己用 `FB_EnOceanSTM100Generic` 拿 raw byte 时手动解码。

**典型陷阱**：
- 期待"返回档位编号 INT (0..4)"——返回是结构体不是 INT；要拿数字可以包一层 CASE。
- 五位都 FALSE 视为"未收到帧"或"字节损坏"——首帧前的初始状态。

## 4. 错误码 / 返回值

返回值类型 `STREnOceanTurnSwitch`，无错误码。极端输入：

| 输入 | 返回 | 说明 |
|---|---|---|
| 旋钮档 Auto 对应的 byte | `bStageAuto = TRUE` | 其余 FALSE |
| 档 0..3 对应的 byte | 对应 `bStage_x = TRUE` | 其余 FALSE |
| 损坏 / 未定义 byte | 可能 5 位全 FALSE | 工程上需要识别此情况 |

## 5. 使用注意 / 常见坑

- **互斥不要假设**：理论上只有一位 TRUE，但工程上仍要写"未识别"分支（默认设回 Auto 或停车安全模式）。
- **配合 `FB_EnOceanSTM100Generic`**：`stTurn := F_Byte_to_TurnSwitch(byData := fbSTM.nDataBytes[2]);` —— byte 2 通常是旋钮位（具体看设备手册）。
- **配合 `FB_Rec_Generic`**：KL6581 体系下用 `stTurn := F_Byte_to_TurnSwitch(byData := fbRec.ar_Value[2]);`
- **首帧前 5 位都 FALSE**：和其他 EnOcean 解码一样，上电后到收第一帧之前是未知态。
- **HVAC 联动**：典型映射 `bStage_0`→关空调；`bStage_1`→节能模式；`bStage_2`→舒适模式；`bStage_3`→Boost；`bStageAuto`→由 BMS 调度。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_Byte_to_TurnSwitch.TcPOU`](../examples/P_Demo_F_Byte_to_TurnSwitch.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_F_Byte_to_TurnSwitch
VAR
    byRaw     : BYTE;
    stTurn    : STREnOceanTurnSwitch;
END_VAR
stTurn := F_Byte_to_TurnSwitch(byData := byRaw);
```

## 7. 业务场景与实际价值

- **场景**：房间温控面板带 5 档旋钮（Auto / 0 / 1 / 2 / 3）。工程师用 `FB_EnOceanSTM100Generic` 接面板拿到 4 byte 原始数据后，要解码 byte 2 的旋钮位。本函数一次解出 5 位互斥布尔，应用层并列 IF 写各档位的 HVAC 策略，比 `CASE byRaw OF ... END_CASE` 解出枚举更直观一点。
- **价值**：原始字节解码"5 档旋钮"在 EnOcean 协议里不是简单的 0..4 整数（可能有保留位 / 校验），本函数把厂家协议细节屏蔽掉，应用层只看 5 位布尔。
- **替代方案对比**：
  - 用 `FB_EnOceanSTM100`（已废弃）直接给 `E_EnOceanRotarySwitch` 枚举：硬编码字段不灵活
  - 自己写 `CASE byData OF ... END_CASE`：要懂协议字节编码，几乎重做本函数
  - **本函数**：通用 + 简洁 + 与 `FB_EnOceanSTM100Generic` 配套

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173296267.html
- **相关**：`STREnOceanTurnSwitch`（返回结构 §4.2.2.2.8）、`E_EnOceanRotarySwitch`（等价枚举形式 §4.2.1.1.2）、`F_Byte_to_Temp`（同节温度版函数）、`FB_EnOceanSTM100Generic`（典型上游使用者）
