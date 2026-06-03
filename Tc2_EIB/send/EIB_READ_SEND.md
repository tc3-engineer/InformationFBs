# EIB_READ_SEND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Send` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187784971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_EIB_READ_SEND.TcPOU`](../examples/P_Demo_EIB_READ_SEND.TcPOU) |

---

## 1. 功能简述

**发送 EIB Read_Group_Req（主动查询）** 到指定组地址，请求所有挂在该地址的设备回传当前值。本 FB 只发请求；**回应数据由对应的 `EIB_*_REC` FB 接收**（接收 FB 也必须订阅这同一个 `Group_Address`）。

**典型用法**：PLC 启动后想知道楼宇里现有的灯 / 调光器当前状态，调本 FB 发 read_req 到那些组地址，对应设备会主动回应——比等设备自己周期推送快得多。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Group_Address : EIB_GROUP_ADDR;
    bRead         : BOOL;
    str_Rec       : EIB_REC;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Group_Address` | `EIB_GROUP_ADDR` | — | **要查询数据的组地址**（不是要发送数据的目标）。**必须在 KL6301 过滤器内**，否则收不到响应 |
| `bRead` | `BOOL` | — | 上升沿触发：FB 发一帧 Read_Group_Req 到 EIB 网络，请求所有挂在该 group 的设备回传当前值 |
| `str_Rec` | `EIB_REC` | — | 胶水结构，传 `KL6301.str_Data_Rec` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError        : BOOL;
    iErrorID      : EIB_ERROR_CODE;
    bBusy         : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | 出错 |
| `iErrorID` | `EIB_ERROR_CODE` | 错误码 |
| `bBusy` | `BOOL` | FB 活动期间为 TRUE，发送完成 / 失败后回 FALSE |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bRead` 上升沿触发一次 Read_Group_Req。`bBusy` 期间忽略新触发。

**响应不由本 FB 接收**：被查的设备会发回普通 telegram，需要对应类型的 `EIB_*_REC` FB（订阅同 `Group_Address`）接收。PDF 明确 `To receive a response, the group address must be entered in the filter!` ——KL6301 过滤器必须包含该地址，否则响应会被丢。

**与 KL6301 依赖**：必须 `bReady = TRUE`；同 PLC 任务；`str_Rec` 传同一实例；`Group_Address` 必须在过滤器内。

## 4. 错误码 / 返回值

| 枚举值 / 16# | 含义 | 常见原因 |
|---|---|---|
| `NO_EIB_ERROR` / 0 | 无错 | — |
| `WRONG_EIB_DATA_LEN` / 20 | 发送数据长度异常 | 库内部检测，正常使用不应触发 |
| `ERROR_EIB_NO_ACK` / 16#0BBB | EIB 端没有收到目标设备的 ACK | 目标组地址在 EIB 网络上无任何 ACK 设备 / 总线段不通 |
| `WATCHDOG_ERROR_NO_SEND` / 104 | 看门狗判定本帧未发出 | KL6301 长时间忙、被低优先级帧拖死；失败的 group address 写入 `KL6301.NotSendGroup` 局部变量供调试 |
| `KL6301_TP_TOGGLE_ERROR` / 30 | KL6301 1 秒未响应 toggle | KL6301 已死锁；触发 `KL6301.bActivate := FALSE` 再 TRUE 重参数化 |
| `ERROR_EIB_NO_COM_TO_TP` / 16#FAFB | EIB 物理层失联 | KL6301 EIB 侧硬件 / 电源故障 |
| `ERROR_TP_*` / 16#0FCC..16#87CC | KL6301 物理层各类错 | 见 §4 错误码完整表，多为现场布线 / 干扰问题 |

参见 `EIB_ERROR_CODE` 枚举完整定义（PDF §4.3.1.1）。


## 5. 使用注意 / 常见坑

- **只在数据变化时发送**：写 `iData := iData` 不会触发 telegram。要强制重发用对应 `_EX` 版本的 Polling 模式。
- **最小发送间隔由库固化**：在间隔内的连续变化会被合并；中间值会丢。需要精细控制就用 `_EX` 版本。
- **`Group_Address` 不在 KL6301 过滤器内 → 静默丢弃**：写值看似成功但 EIB 网上没出帧。
- **必须 `KL6301.bReady = TRUE`** 才能开始发送；启动前调用本 FB 不会出错但也不会发。
- **与所有 EIB FB 在同一 PLC 任务**：跨任务 EIB_REC 状态不一致，发送丢失。
- **EIB 网络高负载时会触发 `WATCHDOG_ERROR_NO_SEND` (104)**：本帧未发出，失败的 group address 记录在 `KL6301.NotSendGroup` 局部变量供调试。（工程经验补充）
- **`Group_Address` 是「要查的」地址，不是「要发的」地址**：与其它 SEND FB 语义相反，新手易混淆。
- **响应要靠对应的 `_REC` FB**：本 FB 不收响应，业务上要并行挂一个相同 `Group_Address` 的 _REC。
- **`Group_Address` 必须在 KL6301 过滤器内**：否则即便对端发回响应也被 KL6301 丢；PDF 明确警告。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EIB_READ_SEND.TcPOU`](../examples/P_Demo_EIB_READ_SEND.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_EIB_READ_SEND
VAR
    fb       : EIB_READ_SEND;
    stEibRec : EIB_REC;
    stGroup  : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 2, NUMBER := 3);
    bRead    : BOOL;
END_VAR
fb(Group_Address := stGroup, bRead := bRead, str_Rec := stEibRec);
```

## 7. 业务场景与实际价值

- **场景**：主动同步设备当前状态（启动、失同步恢复、HMI 刷新）
- **价值**：唯一发起 EIB read 请求的 FB；比等设备自报快
- **替代方案对比**：
  - 等设备自己周期推送：慢且不可控
  - 本 FB：主动同步的唯一方式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.5.27
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187784971.html
- **相关**：对应 `EIB_*_REC`（接收响应）、`EIB_ALL_DATA_TYPES_REC`（识别 `bEIB_READ`）、`EIB_ALL_DATA_TYPES_SEND` (`bReadCommand = TRUE` 对方答 read 用)
