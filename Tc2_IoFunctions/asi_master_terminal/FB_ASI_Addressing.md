# FB_ASI_Addressing

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59149579.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ASI_Addressing.xml`](../examples/P_Demo_FB_ASI_Addressing.xml) |

---

## 1. 功能简述

AS-Interface（ASI / AS-i）现场总线上为 slave 重新编址：把 slave 当前地址（`iOldAddress`）改成新地址（`iNewAddress`）。常用于现场更换 slave 后写新地址（新出厂的 ASI slave 地址默认 0）。本 FB 与其它 ASI FB 一样，依赖 `FB_ASI_ParameterControl` 在后台调度通讯。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iOldAddress : BYTE;
    iNewAddress : BYTE;
    bStart : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iOldAddress` | `BYTE` | 当前 slave 地址。新出厂 slave 默认地址为 0。范围：标准 ASI = 0..31，A/B 扩展 = 0..62 (0x00..0x3E)。 |
| `iNewAddress` | `BYTE` | 要写入 slave 的新地址。 |
| `bStart` | `BOOL` | 上升沿触发一次编址命令；调用期间保持高电平，完成后由用户清零。 |

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
| `bErrornumber` | `DWORD` | ASI 主端子返回的命令专用错误码（DWORD）。具体值参见 KL6201 / EL6201 手册的 ASI master command error 表。0 = 无错。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stParameterBuffer : ST_ParameterBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stParameterBuffer` | `ST_ParameterBuffer` | ASI FB 共享后台通讯缓冲；所有 ASI FB 实例 + `FB_ASI_ParameterControl` 必须 IN_OUT 传入同一实例。 |

## 3. 行为说明

`bStart` 上升沿触发：FB 把"编址命令"放到 `stParameterBuffer` 共享缓冲里等 `FB_ASI_ParameterControl` 取走、经过 ASI 主端子的过程数据发到 slave。`bBusy := TRUE`（命令已被接受、放入队列），slave 接收后修改自己的地址并应答。完成后 `bBusy := FALSE`；若过程出错 `bErr := TRUE`、`bErrornumber` 给出 ASI 主端子的错误码（参见 KL6201 手册的命令错误码表）。**注意**：ASI slave 地址范围 1..31（标准 ASI）或 1A..31B（A/B 扩展）。新出厂 slave 地址 = 0，必须先用本 FB 编址才能正常通讯。

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
- 一次只能给一台未编址的 slave 编址：若总线上有多个地址 0 的 slave 同时上电，编址会失败或随机命中其中一台。**实际现场操作流程**：先单独接入一台新 slave 编址 → 断开 → 再接下一台。（工程经验补充）
- 编址成功后 slave 把新地址保存到自己 EEPROM，下次上电用新地址；不要反复编址（EEPROM 寿命）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ASI_Addressing.xml`](../examples/P_Demo_FB_ASI_Addressing.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：更换故障的 ASI 流量计：取下旧 slave（旧地址 5），装新 slave（出厂默认 0），用本 FB 把它从 0 编址为 5。这样工程程序的引用关系不变。
- **价值**：不必拆机柜插 ASI 编址手持工具——直接 PLC 程序 + HMI 按钮完成现场更换设备。
- **替代方案对比**：
  - 手持 ASI 编址器：要拆下 slave 接到手持器上编址再装回，繁琐
  - **本 FB**：直接在线编址，机柜不动手

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59149579.html
- **相关 FB / FC**：`FB_ASI_ParameterControl`, `FB_ASI_SlaveDiag`, `FB_ASI_ReadParameter`
