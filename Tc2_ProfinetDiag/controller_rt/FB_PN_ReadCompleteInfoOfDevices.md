# FB_PN_ReadCompleteInfoOfDevices

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `controller_rt` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14999239435.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_ReadCompleteInfoOfDevices.TcPOU`](../examples/P_Demo_FB_PN_ReadCompleteInfoOfDevices.TcPOU) |

---

## 1. 功能简述

生成 TwinCAT 中已组态的全部 PROFINET 设备的完整信息列表，逐台返回 `ST_PN_DeviceInfo`（BOX 地址、设备名、IP/掩码/网关、PN 状态、诊断、输入/输出 CR 数、循环时间）。适用于 PROFINET RT 控制器（如 TF6271、CCAT M930 接口或 EL6631 v11(v.024)）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bExecute                     : BOOL;
  sControllerName              : T_Maxstring
  tTimeout                     : TIME;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `sControllerName` | `T_MaxString` | PROFINET RT 控制器在 TwinCAT 设备树中的名称。⚠️ PDF/InfoSys 代码块印作 `T_Maxstring`（描述表写 `T_MaxString`），以代码块逐字为准（类型大小写不影响编译别名）。 |
| `tTimeout` | `TIME` | 整个读取过程的超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  nErrorID                : UDINT;
  nDevices                : UINT;
  aInfoOfDevices          : ARRAY [1..255] OF st_PN_DeviceInfo;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `nErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4）。 |
| `nDevices` | `UINT` | 组态中的 PROFINET 设备数。 |
| `aInfoOfDevices` | `ARRAY [1..255] OF st_PN_DeviceInfo` | 已组态各 PROFINET 设备的设置信息数组（逐台一项）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bExecute` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 `nDevices` 与 `aInfoOfDevices` 数组 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`nErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bExecute` 上升沿被接受时才更新，因此读 `bError`/`nErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bExecute` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bExecute` 拉回 FALSE 再拉高。

**与 `FB_PN_ReadStateOfDevices` 的区别**：后者只给总览计数，本 FB 给逐台完整信息（每台一个 `ST_PN_DeviceInfo`），数据量大、耗时更长，故带 `tTimeout` 输入控制整体超时。

## 4. 错误码 / 返回值

`nErrorID` 在 `bError = TRUE` 时返回 ADS 错误号（`bError = FALSE` 时无意义）。下表摘自 PDF §5.1「ADS Return Codes」的常见取值：

| `nErrorID` (dec) | Hex | 名称 | 含义 / 处理建议 |
|---|---|---|---|
| `0` | `0x0` | `ERR_NOERROR` | 无错误，操作成功；读取输出结果 |
| `6` | `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到——`PORT` 错误，或目标 ADS 服务未启动/不可达。检查 `PORT` 与设备状态 |
| `7` | `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标设备未找到——AMS 路由不存在。检查 `NETID` 与路由表 |
| `16` | `0x10` | `ERR_LOWINSTLEVEL` | 授权等级过低（许可证问题） |
| `1280` | `0x500` | `ROUTERERR_NOLOCKEDMEMORY` | 路由锁定内存不足 |
| `1792`+ | `0x700`+ | 一般 ADS 错误 | 命令相关错误（如设备拒绝、参数非法）；可对照 PDF §5.1「General ADS error codes」一节查全 |

> 完整 ADS 返回码表（Global / Router / General ADS / RTime 四组）参见 PDF §5.1 章节。⚠️ PDF 与 InfoSys 均未给出本库各 FB 专属的错误码子集，上表为 ADS 通用码。

## 5. 使用注意 / 常见坑

- **用 `nDevices` 限定遍历范围**：`aInfoOfDevices` 固定 255 项，但只有前 `nDevices` 项有效，遍历时以 `nDevices` 为上界。
- **`tTimeout` 要给足**：逐台读取耗时随设备数增长，超时太小会中途失败；建议按设备数留余量（如每台 1~2 秒）。（工程经验补充）
- **适用控制器**：TF6271 / CCAT M930 / EL6631 v11(v.024) 等 RT 控制器。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_ReadCompleteInfoOfDevices.TcPOU`](../examples/P_Demo_FB_PN_ReadCompleteInfoOfDevices.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_ReadCompleteInfoOfDevices
VAR
    fbReadAll     : FB_PN_ReadCompleteInfoOfDevices;
    bReadAllReq   : BOOL := FALSE;            // 在线上升沿触发
    sCtrlName     : T_MaxString := 'Device 1 (PROFINET RT Controller)';  // 控制器在树里的名字
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
    nDevCount     : UINT;                     // 设备总数
    aDevInfo      : ARRAY [1..255] OF ST_PN_DeviceInfo;  // 逐台明细
END_VAR

// 上升沿触发；读全网逐台明细，超时给 10 秒
fbReadAll(
    bExecute := bReadAllReq,
    sControllerName := sCtrlName,
    tTimeout := T#10S,
    bBusy    => bBusy,
    bError   => bErr,
    nErrorID => nErrId,
    nDevices => nDevCount,
    aInfoOfDevices => aDevInfo
);

// 遍历 1..nDevCount 取每台 aDevInfo[i].sBoxName / sIP_Addr / nCycleTime
```

## 7. 业务场景与实际价值

- **场景**：HMI 设备详情页要列出每个 PROFINET 从站的名称、IP、循环时间、PN 状态，做成可滚动的设备清单。
- **价值**：一次调用拿回全网逐台明细，免去逐设备多次 ADS 读取与字段拼装。
- **替代方案对比**：逐台 `FB_PROFINET_READ_*` 调用既多又慢；本 FB 由控制器一次性汇总返回数组。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.1.3.2 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14999239435.html
- **相关 FB / FC**：`FB_PN_ReadStateOfDevices`（总览计数）、`ST_PN_DeviceInfo`（设备信息结构）
