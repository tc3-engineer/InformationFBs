# FB_BA_KL32xx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / I/O` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785100043.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_KL32xx.TcPOU`](../examples/P_Demo_FB_BA_KL32xx.TcPOU) |

---

## 1. 功能简述

KL3201 / KL3202 / KL3204 / KL3208_0010 电阻输入端子的运行时配置 FB。把所选传感器类型（Pt100、Ni1000、Pt1000 等，通过 `eSensor : E_BA_MeasuringElement` 选择）写入端子寄存器，并周期回读端子状态。FB 直接消费端子的原始过程数据（`nRawState`、`nRawDataIn` 等四个 IN_OUT），把原始值转换成工程量（℃）输出在 `fVal`，并把断线 / 短路诊断输出到 `bWireBreak` / `bShortCircuit`。配合 KL32xx 系列 4 通道电阻输入端子的每通道一个 FB 实例使用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bConfigurate            : BOOL;
    bReadConfig             : BOOL;
    eSensor                 : E_BA_MeasuringElement;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConfigurate` | `BOOL` | 上升沿触发：把当前 `eSensor` 写入端子寄存器，使端子按所选传感器类型工作。 |
| `bReadConfig` | `BOOL` | 上升沿触发：从端子寄存器读出当前配置，用于诊断 / HMI 显示。 |
| `eSensor` | `E_BA_MeasuringElement` | 传感器类型枚举：包含 Pt100 / Pt1000 / Ni100 / Ni1000 / 电阻 (Ohm) 等可选项。详见 `E_BA_MeasuringElement` 定义。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nState                  : USINT;
    nData                   : INT;
    fVal                    : REAL;
    bErr                    : BOOL;
    bWireBreak              : BOOL;
    bShortCircuit           : BOOL;/
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nState` | `USINT` | 端子当前状态字节（来自 `nRawState`）。 |
| `nData` | `INT` | 当前原始过程数据（来自 `nRawDataIn`，未缩放）。 |
| `fVal` | `REAL` | 工程量值。Pt100 / Pt1000 / Ni 系列时单位 ℃；纯电阻档时单位 Ω。已按所选 `eSensor` 缩放。 |
| `bErr` | `BOOL` | 端子配置出错（写入校验失败或读回 `eSensor` 与下发不符）。 |
| `bWireBreak` | `BOOL` | TRUE = 检测到断线（端子上报 wire break 位）。 |
| `bShortCircuit` | `BOOL` | TRUE = 检测到短路（端子上报 short circuit 位）。⚠️ PDF VAR 区此处印刷为 `bShortCircuit : BOOL;/` 末尾多一个斜杠 `/`，是 PDF 印刷错误；InfoSys 与编译器都接受 `BOOL`。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    nRawState               : USINT;
    nRawDataIn              : INT;
    nRawCtrl                : USINT;
    nRawDataOut             : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nRawState` | `USINT` | 链接到端子状态字节（输入侧 `%I*`），承载端子上报的 status + 诊断位。 |
| `nRawDataIn` | `INT` | 链接到端子的原始数据字（输入侧 `%I*`），即 16-bit 原始 ADC 值。 |
| `nRawCtrl` | `USINT` | 链接到端子控制字节（输出侧 `%Q*`），FB 内部写入配置命令。 |
| `nRawDataOut` | `INT` | 链接到端子的原始数据字（输出侧 `%Q*`），FB 内部写入配置参数。 |

### 属性 (Properties)

| 名称 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `FirmwareVersion` | `WORD` | Get | 端子固件版本。 |
| `SensorName` | `STRING` | Get | 当前配置的传感器名称字符串（如 `"Pt100"`）。 |
| `SpecialType` | `WORD` | Get | 端子特殊型号字（如 `0x010` 标识 -0010 子型号）。 |
| `TerminalDescription` | `STRING` | Get | 端子型号字符串（型号 + 固件简介）。 |
| `TerminalType` | `WORD` | Get | 端子型号字（如 KL3208 对应特定 WORD 值）。 |

## 3. 行为说明

`bConfigurate` 上升沿：FB 把 `eSensor` 选择的传感器类型代码写入端子控制字节（通过 `nRawCtrl` / `nRawDataOut`）。端子接受后内部进入新的测量模式，输出原始数据按新类型解释。`bReadConfig` 上升沿：FB 从端子读回当前配置，更新 `fVal` 缩放系数并刷新 `SensorName` / `TerminalDescription` 等 properties。常用工作模式是：上电时一次 `bConfigurate` 上升沿写入配置，之后每个 PLC 周期循环调用本 FB（无需触发任何边沿）让 `fVal` / `bWireBreak` / `bShortCircuit` 实时刷新——因为端子状态是 IN_OUT 链接，每周期自动同步。断线 / 短路诊断：端子内部检测线缆物理故障并把对应位上报到 `nRawState`，FB 拆解后输出在 `bWireBreak` / `bShortCircuit`——这是 KL32xx 系列端子的硬件能力，PT100 等高阻传感器尤其有用（断线时阻值无穷大、短路时阻值为 0，端子能识别区分）。每个通道必须用独立 FB 实例：4 通道的 KL3208 需要 4 个 FB_BA_KL32xx 实例，各自链到对应通道的 4 个 IN_OUT 端子变量。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` 输出报告配置错误：

| 状态 | 含义 | 处理建议 |
|---|---|---|
| `bErr = FALSE` 且配置已写入 | 配置成功 | 正常运行 |
| `bErr = TRUE` 上升沿后 | 端子配置写入失败或回读校验不一致 | 检查 IN_OUT 是否正确链接到 System Manager 中端子过程数据；检查 `eSensor` 是否被端子型号支持（不支持时回读 `SensorName` 为空或不匹配） |
| `bWireBreak = TRUE` | 物理断线 | 检查传感器接线 |
| `bShortCircuit = TRUE` | 物理短路 | 检查传感器接线 |

PDF + InfoSys 均未列具体错误码（端子诊断字段由硬件直接给出）。

## 5. 使用注意 / 常见坑

- ⚠️ **PDF VAR 区 `bShortCircuit : BOOL;/` 末尾多斜杠**——是 PDF 印刷错误，编译器接受 `BOOL`（InfoSys 一致）。
- **必须链 IN_OUT**：`nRawState` / `nRawDataIn` / `nRawCtrl` / `nRawDataOut` 必须在 System Manager 中 link 到端子的状态字节 / 数据字 / 控制字节 / 数据字（输入 %I* + 输出 %Q*）。**不链则 FB 看不到端子状态**，`fVal` 永远为 0。（工程经验补充）
- **每个通道一个 FB 实例**：KL3208 有 8 个通道（0010 子型号）/ KL3204 有 4 个通道——每个通道 link 自己的 IN_OUT，独立 `FB_BA_KL32xx` 实例。**禁止共用一个实例**（FB 内部状态会被多通道写花）。（工程经验补充）
- 端子上电后默认配置可能不是想要的，**第一次运行必须 `bConfigurate` 上升沿一次**写入正确的 `eSensor`。常用法：PLC 启动逻辑里用 R_TRIG 触发一次。（工程经验补充）
- `fVal` 单位随 `eSensor` 变：温度传感器（Pt/Ni 系列）输出 ℃；纯电阻档输出 Ω。在 SCADA 显示时要按 `eSensor` 切换单位。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_KL32xx.TcPOU`](../examples/P_Demo_FB_BA_KL32xx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：商用建筑暖通系统：每层 4 个 Pt100 温度传感器接在一块 KL3208-0010 上，PLC 周期读温度送给楼控 HMI 与 PID 控制环。要求每路独立的断线 / 短路报警以便快速排查。
- **价值**：本 FB 把"传感器类型选择 + 原始数据缩放 + 故障诊断"一次性封装。对比手算：① `eSensor` 切换不用动 ADC 缩放系数（暖通工程常需要在不同传感器之间切换）；② 断线 / 短路位直接给到布尔输出，无需查端子寄存器手册。
- **替代方案对比**：
  - **直接读端子寄存器 + 手算 Pt100 阻温曲线**：需 ~50 行 ST 代码 + 查传感器表；多通道时代码 4-8 倍膨胀；
  - **使用 KL3208 PDO 模式自带缩放**：System Manager 配置改起来复杂，且诊断位需要单独解码；
  - **本 FB**：BA 库标准方案，配 Tc3_BA2_Common 一行调用搞定。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785100043.html
- **相关枚举**：`E_BA_MeasuringElement`
- **相关库**：`Tc2_IoFunctions.FB_KL320xConfig` / `FB_KL3208Config` / `FB_KL3228Config`（同一系列端子的 Tc2 版配置 FB，本 Tc3 版增加传感器枚举抽象 + 断线/短路独立位）

## 9. 待确认项 (⚠️)

- PDF VAR 区 `bShortCircuit : BOOL;/` 末尾的 `/` 是 PDF 印刷错误；按 InfoSys / 编译器一致，类型是 `BOOL`。本文档照 PDF 原样保留。
