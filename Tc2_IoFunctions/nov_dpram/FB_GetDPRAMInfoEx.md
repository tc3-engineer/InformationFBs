# FB_GetDPRAMInfoEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `NOV/DP-RAM` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2217659019.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetDPRAMInfoEx.xml`](../examples/P_Demo_FB_GetDPRAMInfoEx.xml) |

---

## 1. 功能简述

加强版 NOV / DP-RAM 信息查询。比 `FB_GetDPRAMInfo` 多返回 **访问类型** (`eAccessType`，BYTE / WORD / DWORD)。业务侧可据此选择对应大小的访问方式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nDevId : UDINT;
    bExecute : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nDevId` | `UDINT` | - | 无符号整数 `nDevId`。 |
| `bExecute` | `BOOL` | - | 上升沿触发查询。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    stInfo : ST_NovRamAddrInfoEx;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `stInfo` | `ST_NovRamAddrInfoEx` | NOV-RAM 完整元信息（地址、大小、访问类型）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bExecute` 上升沿触发查询：`bBusy := TRUE`，FB 经 ADS 查 NOV-RAM 完整元信息。完成后 `stInfo` (类型 `ST_NovRamAddrInfoEx`) 含地址指针 + 大小 + 访问类型枚举。若访问类型是 BYTE 对齐（如 CX9000），调用方须用 `FB_NovRamReadWriteEx` 而非直接 MEMCPY，否则会触发异常。若访问类型是 DWORD 或不要求特殊对齐，可直接 MEMCPY。触发语义为上升沿一次性，调用者需要在 `bBusy` 落回后再使用 `stInfo` 内容。

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

- **自 TwinCAT 2.9 build 927 起，retain data 已不再需要本系列 FB**（PDF 明确说明）；本 FB 仅用于早期 FCxxxx-0002 卡的 NOV-RAM 直接访问。
- NOV-RAM 的地址查找在第一次调用 / `nDevId` 改变时通过内部 ADSREAD 进行，**需要几个 PLC 周期**才能拿到地址；之后通过 MEMCPY 直接读写。（工程经验补充）
- NOV-RAM 总长度由 FB 内部检测，**自动限制最大读 / 写长度**，不会越界；但调用方仍应 sanity-check 自己的缓冲不要超过 NOV-RAM 物理大小。（工程经验补充）
- 某些卡的 NOV-RAM 要求 BYTE 或 WORD 对齐访问（如 CX9000），本 FB 用 MEMCPY 直接拷贝时会失败——这种情况要改用 `FB_NovRamReadWriteEx`。（工程经验补充）
- 返回的 `eAccessType` 决定后续访问方式；先用本 FB 查一次再决定用普通 / Ex 读写 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetDPRAMInfoEx.xml`](../examples/P_Demo_FB_GetDPRAMInfoEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：通用 PLC 程序：兼容多种 NOV-RAM 卡（FC3101-0002、CX9000 等），上电时先用本 FB 查访问类型再决定后续访问策略。
- **价值**：通用接口，便于编写跨硬件平台的 PLC 程序。
- **替代方案对比**：
  - `FB_GetDPRAMInfo`：缺访问类型字段
  - **本 FB**：通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.8.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2217659019.html
- **相关 FB / FC**：`FB_GetDPRAMInfo`, `FB_NovRamReadWriteEx`
