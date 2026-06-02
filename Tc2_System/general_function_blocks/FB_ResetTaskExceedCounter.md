# FB_ResetTaskExceedCounter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/11107119115.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ResetTaskExceedCounter.TcPOU`](../examples/P_Demo_FB_ResetTaskExceedCounter.TcPOU) |

---

## 1. 功能简述

FB_ResetTaskExceedCounter 通过 ADS 把指定任务的 Exceed Counter（周期超限计数）清零。Exceed Counter 由 TwinCAT 系统在该任务每次未能在规定周期内完成时递增；本 FB 在调试或回归基线确立后清零，便于观察新基线之后的实时性表现。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute         : BOOL;
    nTaskAdsPort     : UINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次清零。期间保持 TRUE 直到 `bBusy` 回 FALSE 再复位。 |
| `nTaskAdsPort` | `UINT` | - | 目标任务的 ADS 端口号。可用 `TwinCAT_SystemInfoVarList._TaskInfo[GETCURTASKINDEXEX()].AdsPort` 取当前任务端口。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy          : BOOL;
    bError         : BOOL;
    nErrorID       : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | ADS 写操作进行中，期间不接受新的 `bExecute` 上升沿。 |
| `bError` | `BOOL` | 上次执行检测到错误。`bBusy` 落沿后稳定可读。 |
| `nErrorID` | `UDINT` | ADS 错误码；详见 ⚠️『ADS Return Codes』参考表。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须周期调用让内部 ADS 异步状态机推进。`bExecute` 上升沿启动一次清零：`bBusy := TRUE` 直到 ADS 写应答返回；成功后 `bError := FALSE`，下次再去用 `FB_ReadTaskExceedCounter` 读到的值就从 0 重新累积。

**任务端口怎么填**：与 `FB_ReadTaskExceedCounter` 相同：`TwinCAT_SystemInfoVarList._TaskInfo[GETCURTASKINDEXEX()].AdsPort` 取本任务端口，需要清零别的任务改下标。

**典型用法**：与 `FB_ReadTaskExceedCounter` 搭配。运维流程：(1) 修改优化代码 → (2) 调本 FB 清零计数 → (3) 让系统跑 1 小时 → (4) 调 `FB_ReadTaskExceedCounter` 读新增计数。这样不会被历史累计淹没。

## 4. 错误码 / 返回值

`nErrorID` 为标准 ADS 错误码。常见取值参考 ⚠️『ADS Return Codes』参考表（PDF 与 InfoSys 均未在本节列举完整码表）。

## 5. 使用注意 / 常见坑

- 本 FB 自 Tc2_System >= 3.4.25.0 起提供。
- 清零是状态改变性的 ADS 写，建议只在调试或运维断面使用，不要在生产正常态周期触发（会丢历史信息）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ResetTaskExceedCounter.TcPOU`](../examples/P_Demo_FB_ResetTaskExceedCounter.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把 1 ms 任务里的某段 FOR 循环优化后，需要确认新代码不再造成超限；先清零再观察 24 小时计数是否仍为 0。
- **价值**：替代手写 `ADSWRITE` 到任务参数符号；一行调用且自动错误码处理。
- **替代方案对比**：手写 ADSWRITE 需要任务符号句柄维护和错误处理代码，约 30 行；本 FB 替代。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/11107119115.html
- **相关 FB / FC**：`FB_ReadTaskExceedCounter`（同节配对，用于读取）
