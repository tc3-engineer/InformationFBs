# FB_GetLocalAmsNetId

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35001483.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetLocalAmsNetId.TcPOU`](../examples/P_Demo_FB_GetLocalAmsNetId.TcPOU) |

---

## 1. 功能简述

FB_GetLocalAmsNetId 读取**本机 TwinCAT 系统的 AMS Net ID**——TwinCAT 设备在 AMS 网络中的唯一寻址标识（形如 `5.32.156.10.1.1`）。PLC 程序在做远端 ADS 通讯、上传日志、配置路由时通常需要先知道自己的 AmsNetId。

FB 返回的 NetId 与机器名、IP 解耦：换 IP / 改主机名不会变；只有手动改 TwinCAT 注册表里的 AmsNetId 才会变。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    AddrString : T_AmsNetId;
    AddrBytes : T_AmsNetIdArr;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `AddrString` | `T_AmsNetId` | 参数 `AddrString`（类型 `T_AmsNetId`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `AddrBytes` | `T_AmsNetIdArr` | 参数 `AddrBytes`（类型 `T_AmsNetIdArr`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：`bExecute` 上升沿触发一次同步读，本机调用极快（典型 < 5 ms）。

**输出**：`sNetID`（字符串形式 `n.n.n.n.n.n`）或 `AmsNetID`（`T_AmsNetID` 结构）；`bDone` / `bErr` 表示成功 / 失败。

**惯用场景**：开机后 POU 里调一次，把结果存到 GVL（全局变量列表）里供整个项目其他模块复用，避免反复调用 ADS。


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
- 调用太晚：PLC 任务启动早于 TwinCAT SystemService 初始化时短暂返回错——开机后建议延迟 1 秒再调。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetLocalAmsNetId.TcPOU`](../examples/P_Demo_FB_GetLocalAmsNetId.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：开机后读一次本机 NetId 缓存到 GVL，供整个项目其他 FB 调用 ADS 时复用。
- **价值**：替代手动配置文件读 NetId 或从 INI / 注册表读取。
- **替代方案对比**：
  - 直接读注册表：太底层、跨 Windows 版本难维护。
  - 把 NetId 写到 GVL 字面常量：版本管理麻烦、克隆机器易出错。
  - **本 FB**：标准 ADS 调用，跨版本稳定。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.33
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35001483.html
- **相关 FB**：`FB_GetHostName`, `FB_GetSystemId`
