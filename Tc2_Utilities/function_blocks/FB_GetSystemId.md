# FB_GetSystemId

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35003531.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetSystemId.TcPOU`](../examples/P_Demo_FB_GetSystemId.TcPOU) |

---

## 1. 功能简述

FB_GetSystemId 读取**本机 TwinCAT 系统 ID（SystemID）**——一个全局唯一的 16 字节 GUID，与硬件绑定。用于 License 绑定、设备硬件指纹、防克隆校验。

SystemID 由 TwinCAT 安装时根据主板 / CPU / 网卡 MAC 等综合生成，重装系统会变化。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
    sNetId : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    stSystemId : GUID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrorId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `stSystemId` | `GUID` | 参数 `stSystemId`（类型 `GUID`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿读一次。SystemID 以 `GUID` 结构（16 字节）返回，业务侧可转字符串显示或哈希作为机器指纹。

**稳定性**：同一台 PLC 上 SystemID 在 TwinCAT 安装期间稳定；重装 TwinCAT / 更换硬件会变。

**典型用法**：自研 License 系统拿 SystemID 做加密种子，校验通过才允许 PLC 进入 Run 模式。


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
- **不要假设跨重装稳定**——SystemID 重装 TwinCAT 会变；做长期 License 应以 dongle 或硬件序列号为准（参考 FB_GetDongleSystemID）。
- SystemID 长度 16 字节，转字符串后 32-36 字符；HMI 显示截短前 8 字符可读性即可。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetSystemId.TcPOU`](../examples/P_Demo_FB_GetSystemId.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：自研 License 系统校验：客户拿 SystemID 来要密钥，密钥与 SystemID 绑定。
- **价值**：比 MAC / 主板 SN 更适合 TwinCAT 软件授权。
- **替代方案对比**：
  - 用 MAC 地址：网卡换 / 虚拟机克隆易绕过。
  - 用主板 SN：需 Windows API 跨版本兼容性麻烦。
  - **本 FB**：TwinCAT 内置，授权直接绑 TwinCAT 实例。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.36
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35003531.html
- **相关 FB**：`FB_GetVolumeId`, `FB_GetDongleSystemID`, `FB_CheckLicense`
