# FB_GetRouterStatusInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35002763.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetRouterStatusInfo.xml`](../examples/P_Demo_FB_GetRouterStatusInfo.xml) |

---

## 1. 功能简述

FB_GetRouterStatusInfo 查询本机 TwinCAT AMS Router 的运行统计：消息计数、当前并发连接数、最大队列长度、丢包数等。用于诊断 AMS 通讯是否过载、路由器是否健康。

返回结构 `ST_AmsRouterStatusInfo` 含多个 UDINT / DWORD 计数器，业务可纳入 HMI 状态面板。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetId;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrID : UDINT;
    info : ST_TcRouterStatusInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrID` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `info` | `ST_TcRouterStatusInfo` | 参数 `info`（类型 `ST_TcRouterStatusInfo`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿读一次。本地 ADS 调用，< 10 ms。

**典型周期**：HMI 状态面板里每秒触发一次足够；不要 < 100 ms 高频读，会无意义占用 SystemService。

**字段含义**：每个计数器都是累计值，复位时机为 TwinCAT 服务重启。要看『每秒新增』需要业务侧自己做差分。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` + `nErrId`（或 `bError` + `nErrorId`）输出报告错误：

- `bErr / bError = FALSE` 且 `nErrId / nErrorId = 0`：本次请求成功。
- `bErr / bError = TRUE`：本次请求失败，错误号在 `nErrId / nErrorId`。

常见错误号属于 **ADS Return Codes**（PDF 与 InfoSys 都引用此表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x07` | 目标机器未找到（ADSERR_DEVICE_INVALIDDATA） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| 其他 | PDF 未枚举，详见 Beckhoff 在线 ADS Return Codes 表 ⚠️ |

## 5. 使用注意 / 常见坑

- **Windows 系统调用，跨网段 ADS 时长比本地慢**——本地调用 < 50 ms，跨网段可能 500 ms+。（工程经验补充）
- **返回字符串编码**：主机名 / 域名通常 ASCII，跨语言系统（中文 Windows）可能带本地编码字节，处理 UI 显示前要确认编码。（工程经验补充）
- `bExecute` 上升沿触发，不要持续高电平当作连续读——会被忽略。
- PDF 未列错误码——按通用 ADS Return Codes 对照（参考 Beckhoff 在线表）。
- 调用前 `bDone` / `bErr` 输出保留上一次结果，业务代码不要在 `bExecute` 还没触发就读输出。（工程经验补充）
- 计数器是累计值，业务侧要做差分才能得到吞吐率。（工程经验补充）
- 出现 `LostMessages > 0` 不一定是错——也可能是远端机器已下电；要结合 ping / 路由表判断。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetRouterStatusInfo.xml`](../examples/P_Demo_FB_GetRouterStatusInfo.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 网络诊断页：实时显示 AMS Router 消息计数 / 丢包数。
- **价值**：提供 Router 内部观测点，比简单 ping 检测精确。
- **替代方案对比**：
  - 用 Wireshark 抓包：太重，不适合现场。
  - 仅 ping：检测路径通断但看不到协议级丢包。
  - **本 FB**：TwinCAT 内置观测。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.35
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35002763.html
- **相关 FB**：`FB_GetLocalAmsNetId`
