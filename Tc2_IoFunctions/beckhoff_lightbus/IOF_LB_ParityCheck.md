# IOF_LB_ParityCheck

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Beckhoff Lightbus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59108747.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_LB_ParityCheck.TcPOU`](../examples/P_Demo_IOF_LB_ParityCheck.TcPOU) |

---

## 1. 功能简述

Beckhoff Lightbus 读取所有模块的奇偶错误计数器（每模块一个 8 bit 计数器，无溢出）。**不复位** 计数（如要复位见 `IOF_LB_ParityCheckWithReset`）。最多 256 个计数（即最多 256 模块）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    LEN : UDINT;
    DESTADDR : PVOID;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `LEN` | `UDINT` | - | 要读的模块计数（字节数 = 计数器个数）。 |
| `DESTADDR` | `PVOID` | - | 数据缓冲区地址，用 `ADR()` 运算符取得。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

调用前用户准备一个 `ARRAY[1..N] OF BYTE` 缓冲区（N = 要读的模块数）并把 `DESTADDR := ADR(buffer)`、`LEN := N`。`START` 上升沿触发一次读：`BUSY := TRUE`，FB 经 ADS 把 N 个奇偶计数器读到缓冲区。完成后 `BUSY := FALSE`，`buffer[k]` = 模块 k 的奇偶错误累积值。由于计数器不溢出，长时间运行的环可能某些模块累积到 255 后停在 255——这本身不是故障，只是已饱和。想看相对增长率，需要定期用 `IOF_LB_ParityCheckWithReset` 复位。

## 4. 错误码 / 返回值

本 FB 通过 `bError` / `ERR` + `nErrId` / `ERRID` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`。

常见错误号（按 ADS Return Codes 表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）—— 设备未启用或 DeviceId 错 |
| `0x07` | 目标机不在线（ADSERR_DEVICE_NOTREADY） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）—— `TMOUT` 太短或现场总线响应慢 |
| 其他 | 见 Beckhoff **ADS Return Codes** 在线表，及现场总线主站特有的错误码（PDF 未列入本节） |

⚠️ PDF / InfoSys 未在本 FB 处列具体的现场总线错误号，需配合主站手册查询。

## 5. 使用注意 / 常见坑

- Beckhoff Lightbus 是早期光纤总线，**TwinCAT 3 已不再支持** Lightbus 主站硬件（C1220 ISA / FC200x PCI）。PDF 明确说 "not supported by TwinCAT 3 at present"。
- 本系列 FB 仅供老工程升级到 TwinCAT 3 后做"代码兼容性参考"，**实际运行需要 TwinCAT 2 或更早**。
- ADS 错误号见 Beckhoff **ADS Return Codes** 在线表；具体光纤错误码 PDF 未列入本节。（工程经验补充）
- 计数器**不溢出**：到 255 后会停止累积；长时间不复位时数据失去时间分布信息。（工程经验补充）
- PDF 中 `LEN` VAR 区写 `UDINT`、描述列写 "UINT"，以 VAR 区为准。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_LB_ParityCheck.TcPOU`](../examples/P_Demo_IOF_LB_ParityCheck.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Lightbus 长期运行：周期（每天一次）读所有模块的奇偶错计数，趋势异常时报警。
- **价值**：把光纤层错误监控做成可程序化采集，写入历史库做趋势分析。
- **替代方案对比**：
  - 直接读 Lightbus 主站寄存器：底层繁琐
  - **本 FB**：标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59108747.html
- **相关 FB / FC**：`IOF_LB_ParityCheckWithReset`, `IOF_LB_BreakLocationTest`
