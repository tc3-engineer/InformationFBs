# F_IOPortWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `I/O port access` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31027595.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_IOPortWrite.TcPOU`](../examples/P_Demo_F_IOPortWrite.TcPOU) |

---

## 1. 功能简述

F_IOPortWrite 直接写一个值到 PC 主板的 I/O 端口。**可能损坏硬件或数据**：PDF NOTICE 明确警告——写错端口可能导致系统崩溃、硬件损坏甚至 SSD 数据丢失。正确使用前必须明确目标端口的硬件含义。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nAddr : UDINT;
    eSize : E_IOAccessSize;
    nValue : DWORD;
    freq : DWORD := 10000;
    tDuration : TIME := T#1s;
    bExecute : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nAddr` | `UDINT` | - | I/O 端口地址（16 位 I/O 空间）。 |
| `eSize` | `E_IOAccessSize` | - | 写入宽度（`IOAS_BYTE` / `IOAS_WORD` / `IOAS_DWORD`）。 |
| `nValue` | `DWORD` | - | 要写入的值（最大 32 位，高位被 `eSize` 截断）。 |
| `freq` | `DWORD` | `10000` | 无符号整数：`freq`。 |
| `tDuration` | `TIME` | `T#1s` | 时间值：`tDuration`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；`bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` 给出。 |
| `nErrID` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 ADS Return Codes。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，写入立刻完成并返回 BOOL 表示是否调用成功（不代表硬件实际反应正确）。

**端口宽度 `eSize`**：与 `F_IOPortRead` 一致：`IOAS_BYTE` / `IOAS_WORD` / `IOAS_DWORD`。

**返回值**：`TRUE` = 调用层面成功（API 接受了请求）；`FALSE` = API 调用本身失败（如权限不足）。返回 TRUE 不等于硬件按预期工作。

**只在 PC / IPC 上有效**：Embedded Arm 控制器无标准 x86 I/O 端口空间。

**PC 蜂鉣器示例**：PDF 用 PC 蜂鉣器（端口 0x42 / 0x43 / 0x61）演示 `FB_Speaker` 的实现，是本函数最常见的合法用例。

## 4. 错误码 / 返回值

本函数返回 `BOOL`：

| 返回值 | 含义 |
|---|---|
| `TRUE` | 调用成功 |
| `FALSE` | 调用失败（参数错误或硬件故障） |

## 5. 使用注意 / 常见坑

- **写错端口可能毁硬件**：随意试探地址极其危险，可能写入 BIOS / 芯片组寄存器导致永久损坏。**永远**查硬件 datasheet 确认地址。
- **返回 TRUE 不等于硬件响应**：API 接受不代表硬件按预期；要验证效果需用 `F_IOPortRead` 回读或外部测量。
- **多任务竞争**：同一端口被多个任务同时写，结果不可预期；需要用 `TestAndSet` 或全局互斥保护。（工程经验补充）
- **TwinCAT IO Driver 更安全**：标准 EtherCAT 终端有硬件级保护，远比直接端口写安全。新工程不建议用本函数。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_IOPortWrite.TcPOU`](../examples/P_Demo_F_IOPortWrite.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：实现 PC 蜂鉣器报警声：通过写主板蜂鉣器控制端口产生固定频率声波，用于声音提示。
- **价值**：不依赖外部 EtherCAT 蜂鉣模块，纯软件触发 PC 内部蜂鉣器；省一个硬件通道。
- **替代方案对比**：
  - EtherCAT 数字输出 + 外置蜂鉣器：硬件方案，更可靠但要额外接线。
  - Windows `Beep()` 通过 WinAPI：可行但 PLC 调 WinAPI 要写 wrapper。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31027595.html
- **相关 FB / FC**：`F_IOPortRead`, `LPTSIGNAL`
