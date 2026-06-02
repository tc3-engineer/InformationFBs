# FB_KL1501Config

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bus Terminal configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084379019.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL1501Config.TcPOU`](../examples/P_Demo_FB_KL1501Config.TcPOU) |

---

## 1. 功能简述

配置 KL1501（1 通道计数器端子）：选择计数器类型（32 bit 上下计数 / 2×16 bit 上计数 / 32 bit 门控计数 (Low/High 禁用)）+ 选择反向计数。配置过程是把这些设置写到 KL1501 内部寄存器，并读回校验。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bConfigurate : BOOL;
    bReadConfig : BOOL;
    iSetCounterType : INT;
    bSetBackwardCounting : BOOL;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConfigurate` | `BOOL` | 上升沿启动写配置序列：先读端子通用信息 → 写配置寄存器 → 读回校验。 |
| `bReadConfig` | `BOOL` | 上升沿启动只读序列：读端子通用信息 + 当前配置参数。 |
| `iSetCounterType` | `INT` | 计数器类型：0=32bit 上下 1=2×16bit 上 2=32bit 门控(Low 禁用) 3=32bit 门控(High 禁用)。 |
| `bSetBackwardCounting` | `BOOL` | TRUE = 反向计数。 |
| `tTimeout` | `TIME` | 端子配置 / 读取必须在此时长内完成。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    iErrorId : UDINT;
    iState : USINT;
    iDataIn0 : UINT;
    iDataIn1 : UINT;
    iDataIn : UDINT;
    iTerminalType : WORD;
    iSpecialType : WORD;
    iFirmwareVersion : WORD;
    sDescription : STRING;
    sCounterType : STRING;
    bBackwardCounting : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `iErrorId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `iState` | `USINT` | 端子状态字节。 |
| `iDataIn0` | `UINT` | 通道 0 当前计数值（用于 2×16bit 模式）。 |
| `iDataIn1` | `UINT` | 通道 1 当前计数值（同上）。 |
| `iDataIn` | `UDINT` | 组合 32bit 计数值（32bit 模式）。 |
| `iTerminalType` | `WORD` | 端子型号编码（应为 KL1501 对应的值）。 |
| `iSpecialType` | `WORD` | 端子特殊版本。 |
| `iFirmwareVersion` | `WORD` | 无符号整数 `iFirmwareVersion`。 |
| `sDescription` | `STRING` | 字符串参数 `sDescription`。 |
| `sCounterType` | `STRING` | 字符串参数 `sCounterType`。 |
| `bBackwardCounting` | `BOOL` | 布尔标志 `bBackwardCounting`。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stInData : ST_KL1501InData;
    stOutData : ST_KL1501OutData;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stInData` | `ST_KL1501InData` | 端子输入过程映像，IN_OUT 链到 System Manager。 |
| `stOutData` | `ST_KL1501OutData` | 端子输出过程映像，IN_OUT 链到 System Manager。 |

## 3. 行为说明

本 FB 有两种命令：`bConfigurate` 上升沿 = 写配置（先读端子通用数据 → 写配置寄存器 → 读回校验 → 输出到 FB 输出）；`bReadConfig` 上升沿 = 仅读配置（不写）。两者执行期间 `bBusy := TRUE`，期间不接受第二个命令。`iSetCounterType` 取值含义：0 = 32 bit 上下计数；1 = 2×16 bit 上计数；2 = 32 bit 门控计数（gate Low 禁用）；3 = 32 bit 门控计数（gate High 禁用）。`bSetBackwardCounting = TRUE` 反向计数。完成后输出端子的 `iTerminalType` (端子型号编码)、`iSpecialType` (特殊版本)、`iState` (状态)、`iDataIn0` / `iDataIn1` / `iDataIn` (当前计数值)。出错时 `bError := TRUE`、`iErrorId` 给出 KL Config 错误号。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **写端子寄存器会改 EEPROM**，**不要循环周期调用 `bConfigurate`**——EEPROM 寿命 10 万次写入。上电时配置一次足够。
- `stInData` / `stOutData` 必须 IN_OUT 链到 System Manager 中端子的过程数据区，否则 FB 与端子之间通讯不通。（工程经验补充）
- PDF 指出"本 FB 不遵循 alternative output format"——意思是过程数据在标准 vs alternative 模式下偏移不同，FB 假定**标准模式**；若 System Manager 中端子设为 alternative 会出错。（工程经验补充）
- `tTimeout` 默认未指定时建议给 ≥ 2 秒，K-bus 端子配置握手较慢。（工程经验补充）
- 错误号 `iErrorId` 见 PDF 5.6 节的 KL Config 错误码表（如端子型号不匹配 / 寄存器写失败）；具体表 PDF 在每个 FB 后会列。（工程经验补充）
- 计数器类型改变后端子计数值会清零；不要在运行中改类型。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL1501Config.TcPOU`](../examples/P_Demo_FB_KL1501Config.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：印刷线 KL1501 计数器端子：上电时把端子配为 32 bit 上下计数（type 0）+ 不反向，配套编码器接到端子。
- **价值**：把端子配置代码化，避免现场用 KS2000 工具人工拨号。
- **替代方案对比**：
  - KS2000 配置工具：要带工具到现场
  - 直接读写端子寄存器：底层繁琐
  - **本 FB**：上电一次完成配置

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084379019.html
- **相关 FB / FC**：`FB_ReadCouplerRegs (Tc2_Coupler)`, `ReadWriteTerminalReg (Tc2_Coupler)`
