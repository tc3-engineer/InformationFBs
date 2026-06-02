# FB_NovRamReadWriteEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `NOV/DP-RAM` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59132939.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NovRamReadWriteEx.TcPOU`](../examples/P_Demo_FB_NovRamReadWriteEx.TcPOU) |

---

## 1. 功能简述

加强版 NOV-RAM 读 / 写。比 `FB_NovRamReadWrite` 多两点：① 可指定读 / 写偏移 (`nReadOffs` / `nWriteOffs`)，不必从 0 开始；② 自动检测 NOV-RAM 是否需要 BYTE / WORD 对齐访问，必要时改用逐字节拷贝（如 CX9000 NOVRAM 只允许 BYTE 访问）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nDevId : UDINT;
    bRead : BOOL;
    bWrite : BOOL;
    cbSrcLen : UDINT;
    cbDestLen : UDINT;
    pSrcAddr : PVOID;
    pDestAddr : PVOID;
    nReadOffs : UDINT;
    nWriteOffs : UDINT;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nDevId` | `UDINT` | - | 无符号整数 `nDevId`。 |
| `bRead` | `BOOL` | - | 布尔标志 `bRead`。 |
| `bWrite` | `BOOL` | - | 布尔标志 `bWrite`。 |
| `cbSrcLen` | `UDINT` | - | 无符号整数 `cbSrcLen`。 |
| `cbDestLen` | `UDINT` | - | 无符号整数 `cbDestLen`。 |
| `pSrcAddr` | `PVOID` | - | 内存地址指针 `pSrcAddr`（`ADR(buffer)` 取得）。 |
| `pDestAddr` | `PVOID` | - | 内存地址指针 `pDestAddr`（`ADR(buffer)` 取得）。 |
| `nReadOffs` | `UDINT` | - | 读取起始偏移（NOV-RAM 内字节偏移）。 |
| `nWriteOffs` | `UDINT` | - | 写入起始偏移。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbRead : UDINT;
    cbWrite : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `cbRead` | `UDINT` | 无符号整数 `cbRead`。 |
| `cbWrite` | `UDINT` | 无符号整数 `cbWrite`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

工作方式与 `FB_NovRamReadWrite` 类似但更通用：`bRead` 上升沿从偏移 `nReadOffs` 读 `cbDestLen` 字节；`bWrite` 上升沿写 `cbSrcLen` 字节到偏移 `nWriteOffs`。`bRead` 与 `bWrite` 同时拉高时先写后读。本 FB 内部首次调用先用 ADSREAD 查 NOV-RAM 元信息（含访问类型 BYTE/WORD/DWORD），之后按访问类型用 MEMCPY 或逐字节拷贝读写。`bBusy` 反映地址查找 + 命令执行状态；`bErr` / `nErrId` 反映 ADS 错误。

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
- **CX9000 NOVRAM 只允许 BYTE 访问**——必须用本 FB；普通 FCxxx-0002 用 `FB_NovRamReadWrite` 即可。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NovRamReadWriteEx.TcPOU`](../examples/P_Demo_FB_NovRamReadWriteEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX9000 配 NOVRAM：存"批次产量计数"，按批次号偏移存储；写入时按偏移寻址。
- **价值**：支持偏移 + 字节对齐，覆盖 FCxxxx-0002 之外的 NOV-RAM 硬件。
- **替代方案对比**：
  - `FB_NovRamReadWrite`：只能偏移 0，不支持字节对齐
  - **本 FB**：通用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.8.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59132939.html
- **相关 FB / FC**：`FB_NovRamReadWrite`, `FB_GetDPRAMInfoEx`
