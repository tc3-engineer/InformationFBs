# FB_NovRamReadWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `NOV/DP-RAM` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59131403.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_NovRamReadWrite.TcPOU`](../examples/P_Demo_FB_NovRamReadWrite.TcPOU) |

---

## 1. 功能简述

访问 FCxxxx-0002 现场总线卡 NOV-RAM 的读 / 写 FB（老接口）。`bRead` 上升沿从 NOV-RAM 偏移 0 读 `cbDestLen` 字节到 `pDestAddr`；`bWrite` 上升沿把 `pSrcAddr` 处 `cbSrcLen` 字节写到 NOV-RAM 偏移 0。两者同时拉高时先写后读。

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
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nDevId` | `UDINT` | - | 目标 NOVRAM 卡的 DeviceId（System Manager 自动分配）。 |
| `bRead` | `BOOL` | - | 上升沿启动从 NOV-RAM 偏移 0 读 `cbDestLen` 字节到 `pDestAddr`。 |
| `bWrite` | `BOOL` | - | 上升沿启动把 `pSrcAddr` 处 `cbSrcLen` 字节写到 NOV-RAM 偏移 0。 |
| `cbSrcLen` | `UDINT` | - | 写入字节数。 |
| `cbDestLen` | `UDINT` | - | 读取字节数。 |
| `pSrcAddr` | `PVOID` | - | 源数据缓冲地址（用 `ADR()`）。 |
| `pDestAddr` | `PVOID` | - | 目标数据缓冲地址（用 `ADR()`）。 |
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

本 FB 在**第一次调用** 或者 `nDevId` 改变时，内部用 ADSREAD 取 NOV-RAM 物理地址指针（需要几个 PLC 周期）。之后的读写直接 MEMCPY，**单次 PLC 周期内即可完成**（与 retain 写盘的 ms 级延迟不同）。`bRead` 上升沿启动一次读，`bWrite` 上升沿启动一次写。两者同时拉高 → 先写后读，可用于"写 + 校验"模式。`bBusy = TRUE` 表示地址查找尚未完成 / 命令未结束；落回 FALSE 表示动作完成。`bErr` / `nErrId` 反映 ADS 错误号；常见 `0x701` (Service not supported) 表示该卡需要 BYTE 对齐——改用 Ex 版本。`pDestAddr` / `pSrcAddr` 用 `ADR(buffer)` 取得；`cbDestLen` / `cbSrcLen` 用 `SIZEOF(buffer)` 或显式字节数。

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
- **只能从偏移 0 开始读 / 写**；想从指定偏移读 / 写要用 `FB_NovRamReadWriteEx`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_NovRamReadWrite.TcPOU`](../examples/P_Demo_FB_NovRamReadWrite.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 PLC 工程：用 FC3101-0002 卡的 NOV-RAM 存退出时机器姿态（坐标 / 工件计数），下次上电恢复。
- **价值**：替代手写 NOV-RAM 地址映射 + MEMCPY 调用。
- **替代方案对比**：
  - TwinCAT 2.9+ 的 VAR RETAIN：标准做法，无需本 FB
  - `FB_NovRamReadWriteEx`：支持指定偏移 + 字节对齐
  - **本 FB**：早期老工程兼容

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.8.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59131403.html
- **相关 FB / FC**：`FB_NovRamReadWriteEx`, `FB_GetDPRAMInfo`, `FB_GetDPRAMInfoEx`
