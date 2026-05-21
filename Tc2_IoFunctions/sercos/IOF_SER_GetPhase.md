# IOF_SER_GetPhase

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59116171.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_GetPhase.xml`](../examples/P_Demo_IOF_SER_GetPhase.xml) |

---

## 1. 功能简述

读取 SERCOS 环当前的通讯 phase（值 0..4）。上电过程中 phase 会从 0 逐步升到 4（正常运行）；诊断 / 改参数时要先确认 phase 处于正确值。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    GET : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 本机用空串。 |
| `DEVICEID` | `UDINT` | - | SERCOS 主站 Device Id。 |
| `GET` | `BOOL` | - | 上升沿触发一次 phase 读取。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    PHASE : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `PHASE` | `BYTE` | 当前 SERCOS 通讯 phase（0..4）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`GET` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 查 SERCOS 主站当前 phase 字段；完成后 `PHASE` 含当前值（0..4）。触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后才能信任 `PHASE` 值。SERCOS phase 含义：0 = 等待通讯参数；1 = 准备初始化；2 = 通讯参数交换（drive 参数读 / 写在此 phase 进行）；3 = 应用参数交换；4 = 正常运行（cyclic motion）。工程上常用本 FB 周期性查询，确保进入运行模式前 phase 已升到 4。

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

- SERCOS 是早期 motion 总线（SERCANS SCS-P ISA / PCI / Beckhoff FC750x PCI）；现代工程多用 EtherCAT + EL72xx。本系列 FB 用于维护老线。
- SERCOS 通讯有 5 个 phase（0..4），通讯参数访问要求处于特定 phase（通常 phase 2）。（工程经验补充）
- ADS 错误号见 Beckhoff ADS Return Codes 在线表；SERCOS 自定义错误号见对应 IDN 的应答字段。（工程经验补充）
- drive 参数（S / P 参数）通过 IDN（Identification Number）寻址：S = 0..32767，P = 32768..65535。（工程经验补充）
- phase = 0..1 表示主站还在初始化，drive 还没准备好；不要在此期间发 motion 指令。（工程经验补充）
- phase = 2 是参数访问最佳期；phase = 4 是运行期，不能在 phase = 4 改大部分 drive 参数（多数被锁住）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_GetPhase.xml`](../examples/P_Demo_IOF_SER_GetPhase.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS 老线启动诊断：调本 FB 周期性确认 phase 升到 4，否则不允许进入"运行"状态。
- **价值**：让 PLC 程序自动判断 SERCOS 总线是否就绪，避免对未就绪的 drive 发 motion 指令。
- **替代方案对比**：
  - 假设 SERCOS 总是 OK：危险，启动期可能 phase 卡在 1
  - 用 SERCANS 配置工具：要带工具
  - **本 FB**：标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59116171.html
- **相关 FB / FC**：`IOF_SER_SetPhase`, `IOF_SER_ResetErr`, `IOF_SER_IDN_Read`
