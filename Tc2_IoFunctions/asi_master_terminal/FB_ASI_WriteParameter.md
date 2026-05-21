# FB_ASI_WriteParameter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59154187.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ASI_WriteParameter.xml`](../examples/P_Demo_FB_ASI_WriteParameter.xml) |

---

## 1. 功能简述

写 AS-Interface slave 的参数槽（4 bit）。常用于改变 slave 配置（如改变光电传感器的输出极性 / 灵敏度档位）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iParameternumber : WORD;
    iParametervalue : DWORD;
    bStart : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iParameternumber` | `WORD` | ASI 参数编号（slave 内部参数索引）。 |
| `iParametervalue` | `DWORD` | 要写入的参数值（DWORD，但 ASI 标准只用低 4 bit）。 |
| `bStart` | `BOOL` | 上升沿触发一次写命令。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
    bErrornumber : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `bErrornumber` | `DWORD` | ASI 主端子返回的命令专用错误码（DWORD）。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stParameterBuffer : ST_ParameterBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stParameterBuffer` | `ST_ParameterBuffer` | 参数 `stParameterBuffer`（类型 `ST_ParameterBuffer`）。 |

## 3. 行为说明

`bStart` 上升沿触发一次写参数命令：FB 把"写参数"命令排到 `stParameterBuffer`，`FB_ASI_ParameterControl` 在下一个周期取走经 ASI 主端子的过程数据下发到目标 slave。`bBusy := TRUE` 直到命令被 ASI 主端子接受（这只是"接受"，不代表 slave 已经把参数烧进 EEPROM）。完成后 `bBusy := FALSE`；slave 把新参数保存到自己 EEPROM（部分新型 slave 也支持只写 RAM 而不写 EEPROM）。`iParametervalue` 是 DWORD 但 ASI 标准只用低 4 bit。错误时 `bErr := TRUE`、`bErrornumber` 给出 ASI 主端子的命令错误号（参见 KL6201 / EL6201 手册）。

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

- **必须循环调用 `FB_ASI_ParameterControl`**，它是所有 ASI FB 的后台通讯调度器。不调它，其它所有 ASI FB 都不会动。
- `stParameterBuffer : ST_ParameterBuffer` 是全局共享缓冲：所有 ASI FB 实例 + `FB_ASI_ParameterControl` 必须传同一个实例，否则后台调度无法工作。（工程经验补充）
- `stParameter_IN` / `stParameter_OUT` 必须 **链到 System Manager 中 ASI 主端子（如 KL6201 / EL6201）的过程数据**——通过 AT %I* / AT %Q* 映射；不链则 ASI 通讯通道根本没建立。（工程经验补充）
- `bBusy = TRUE` 只表示 *命令被接受*，**不是命令被执行**。具体执行是否完成需要看 `bErr` + `iErrornumber` 在 `bBusy` 落回后的状态。（工程经验补充）
- ASI 命令专用错误码（`bErrornumber` / `iErrornumber`）见 ASI 主端子文档（KL6201/EL6201 手册）——PDF 未列入本节，调用方需要查 ASI master 错误码表。（工程经验补充）
- 参数写入会保存到 slave EEPROM，**不要循环写**（EEPROM 寿命）。
- 改某些参数后 slave 行为可能立刻变化（例如输出极性反转）；写之前确保下游设备做好准备。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ASI_WriteParameter.xml`](../examples/P_Demo_FB_ASI_WriteParameter.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：ASI 光电传感器 slave 5 的输出极性需要在调试期间在线翻转：改参数 1 即可。比拆下来在传感器上拨码开关方便。
- **价值**：免拆装在线改 slave 配置。
- **替代方案对比**：
  - 拨码 / 旋钮：要拆
  - ASI 配置工具：在线但要带工具
  - **本 FB**：PLC 程序内即可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59154187.html
- **相关 FB / FC**：`FB_ASI_ReadParameter`, `FB_ASI_ParameterControl`, `FB_ASI_Addressing`
