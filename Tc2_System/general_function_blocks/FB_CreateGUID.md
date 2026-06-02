# FB_CreateGUID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/12964538507.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CreateGUID.TcPOU`](../examples/P_Demo_FB_CreateGUID.TcPOU) |

---

## 1. 功能简述

FB_CreateGUID 通过 ADS 异步从系统服务生成新的 GUID（128-bit 全局唯一标识符）。如果在 `pGuidBuffer` 上挂载一个 `ARRAY OF GUID`，一次调用即可一次性获取一组新 GUID。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute        : BOOL;
    sNetId          : T_AmsNetId;
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT;
    pGuidBuffer     : POINTER TO GUID;
    nGuidBufferSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次生成。期间保持 TRUE 直至 `bBusy` 落沿。 |
| `sNetId` | `T_AmsNetId` | - | 目标设备 AMS Net ID。本机用空串。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长，默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |
| `pGuidBuffer` | `POINTER TO GUID` | - | GUID 缓冲区首地址。可指向单个 `GUID` 变量或 `ARRAY OF GUID` 第一个元素，由 `ADR()` 取地址。 |
| `nGuidBufferSize` | `UDINT` | - | 缓冲区总字节数，决定一次生成几个 GUID。每个 `GUID` 16 字节。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy    : BOOL;
    bError   : BOOL;
    nErrorId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令执行中。`bBusy = TRUE` 期间不接受新的 `bExecute` 上升沿。 |
| `bError` | `BOOL` | 命令执行过程中出错；`bBusy` 落沿后稳定可读。 |
| `nErrorId` | `UDINT` | `bError = TRUE` 时是 ADS 错误码。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须周期调用让内部 ADS 异步状态机推进。`bExecute` 上升沿启动一次生成：`bBusy := TRUE`，TwinCAT 系统服务异步生成 GUID 并写入 `pGuidBuffer` 指向的缓冲区；完成时 `bBusy := FALSE`。

**一次生成多个 GUID**：`nGuidBufferSize` 是字节数，例如要一次生成 10 个 GUID 就用 `pGuidBuffer := ADR(arrGuids[0]); nGuidBufferSize := SIZEOF(arrGuids);`（前提 `arrGuids : ARRAY[0..9] OF GUID;`）。

**典型用法**：给每个工件、订单、批次打唯一标识；插入数据库主键；OPC UA 节点 NodeId 生成；事件日志条目 ID。

**陷阱**：`pGuidBuffer` 指向局部 / 临时变量在 `bBusy` 期间被释放会写到野指针；务必用全局或实例级变量做缓冲。`nGuidBufferSize` 必须能被 16 整除否则尾部不完整。

## 4. 错误码 / 返回值

`nErrorId` 在 `bError = TRUE` 时是 ADS 错误码。0 = 成功；非 0 时参考『ADS Return Codes』⚠️ 待人工确认；常见 1861 = 调用超时，1809 / 1810 = 句柄或上下文错误。

## 5. 使用注意 / 常见坑

- 本 FB 自 Tc2_System >= 3.4.18.0 起可用。
- `pGuidBuffer` 必须指向异步期间生命周期可保证的内存（全局或 FB 实例成员），否则写野指针会随机崩溃。（工程经验补充）
- `nGuidBufferSize` 应为 16 的整数倍；尾部不足 16 字节的部分系统会忽略。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CreateGUID.TcPOU`](../examples/P_Demo_FB_CreateGUID.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：包装线工艺要求每个出箱件贴含 GUID 二维码用于全生命周期追溯；PLC 在贴标工位前给每件分配 GUID 并写到 MES。
- **价值**：替代手写算法（时间戳 + MAC + 计数器）拼伪 GUID，本 FB 调用系统服务生成符合 RFC 4122 v4 标准的真随机 GUID。
- **替代方案对比**：自己拼组合 ID 容易碰撞或不符合标准；调用 Windows API CoCreateGuid 需要外挂 .NET；本 FB 是 PLC 内首选。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/12964538507.html
- **相关 FB / FC**：`GUID` 类型（同库定义）
