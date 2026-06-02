# FB_SoEWritePassword

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305872267.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEWritePassword.xml`](../examples/P_Demo_FB_SoEWritePassword.xml) |

---

## 1. 功能简述

设置驱动器密码的功能块（Function Block, FB）。它向驱动器写入 SoE 参数 `S-0-0267`（密码），把以 Sercos 字符串形式给出的 `Password` 设进驱动器。

驱动器对部分受保护参数要求先解锁才能写入；`FB_SoEWrite` 自身的 `Password` 形参当前**不起作用**，真正写密码必须用本 FB。典型用法是：在要修改受保护参数之前，先用本 FB 写入正确密码解锁，再用 `FB_SoEWrite` 改参数。

接口形态与库内其它 SoE FB 一致：`Execute` 边沿触发，输出 `Busy`/`Error`/`AdsErrId`/`SercosErrId`，无 `Done`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId    : T_AmsNetID := '';
    Execute  : BOOL;
    Timeout  : TIME := DEFAULT_ADS_TIMEOUT;
    Password : ST_SoE_String;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | `''` | 含 NC 所在 PC 的 AMS NetId 字符串；空串表示本机 |
| `Execute` | `BOOL` | — | 上升沿触发一次写密码 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |
| `Password` | `ST_SoE_String` | — | 以 Sercos 字符串形式给出的密码 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy        : BOOL;
    Error       : BOOL;
    AdsErrId    : UINT;
    SercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `SercosErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次写密码：FB 向驱动器写 `S-0-0267`，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此后驱动器进入"已解锁"状态，受保护参数可写。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId`/`SercosErrId` 给错误码（密码错误一般体现在 `SercosErrId`）。

**解锁参数的完整时序**：① 本 FB 写正确密码解锁 → ② `FB_SoEWrite` 改受保护参数 → ③（视需要）改回非保护状态。`Password` 是 Sercos 字符串，要按驱动器手册规定的密码格式填 `ST_SoE_String`。

**与 `FB_SoEWrite.Password` 的关系**：再次强调——`FB_SoEWrite` 的 `Password` 形参当前未使用，不能靠它解锁；解锁只能用本 FB。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态（见 PDF 示例）。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `SercosErrId : UINT`（Sercos 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、设备不可达、NetId 错 | 检查 EtherCAT OP、`Axis` Link、`NetId` |
| `SercosErrId` ≠ 0 | Sercos 服务错误：密码不正确、格式不符、`S-0-0267` 不支持 | 核对密码值与格式（查驱动器手册），确认驱动器支持密码保护 |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / Sercos 错误码数值。见 Beckhoff ADS Return Codes 总表与驱动器 Sercos 文档。

**清错**：处理完外部原因（如改正密码）后给 `Execute` 新上升沿重试。

## 5. 使用注意 / 常见坑

- **改受保护参数前必须先用本 FB 解锁**：`FB_SoEWrite.Password` 不起作用，这是高频误区。
- **密码格式要符合驱动器规定**：`ST_SoE_String` 内容按手册填，密码错体现在 `SercosErrId`。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：与其它 SoE FB 一致。
- **解锁是会话级状态**：解锁后在该会话内可写受保护参数；驱动器重新上电后通常需重新解锁（工程经验补充）。
- **不要把密码硬编码进可被读取的位置**：密码涉及安全，避免明文留在可导出的源里。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEWritePassword.xml`](../examples/P_Demo_FB_SoEWritePassword.xml)

```iecst
// 场景：改受保护伺服参数前，先写入驱动器密码解锁
rtPwdTrig(CLK := bWritePwdReq);
fbWritePassword(
    NetId    := '',
    Execute  := rtPwdTrig.Q,
    Timeout  := DEFAULT_ADS_TIMEOUT,
    Password := stDrivePassword,
    Axis     := axisServo,
    Busy     => bPwdBusy,
    Error    => bPwdError,
    AdsErrId    => nPwdAdsErr,
    SercosErrId => nPwdSercosErr
);
```

## 7. 业务场景与实际价值

- **场景**：批量改伺服受保护参数前的解锁步骤、产线换型时程序化解锁+改参+锁回、远程维护中解锁特定参数组。
- **价值**：把"解锁驱动器"纳入 PLC 自动化流程，配合 `FB_SoEWrite` 实现无人工干预的受保护参数修改。
- **替代方案对比**：
  - 在 DriveManager 手动输密码解锁：人工、无法自动化
  - 误用 `FB_SoEWrite.Password`：无效，参数仍写不进去
  - **本 FB**：写驱动器密码（`S-0-0267`）的唯一标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305872267.html
- **相关 FB**：`FB_SoEWrite`（解锁后改参数）、`FB_SoERead`（读参数）
