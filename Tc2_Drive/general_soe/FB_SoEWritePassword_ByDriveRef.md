# FB_SoEWritePassword_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307543819.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEWritePassword_ByDriveRef.xml`](../examples/P_Demo_FB_SoEWritePassword_ByDriveRef.xml) |

---

## 1. 功能简述

设置 SoE（Sercos over EtherCAT）驱动器密码的功能块。本 FB 通过 Sercos 参数 `S-0-0267`（password）向驱动器写入一个口令字符串，用于解锁受密码保护的驱动器参数（某些厂商参数、出厂调试参数在写入前要求先解锁）。

密码以 Sercos 字符串类型 `ST_SoE_String` 传入。本 FB 只负责"写密码"这一步，写完之后对受保护参数的实际读写仍由其它 SoE FB（如 `FB_SoEWrite`）完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT;
    sPassword  : ST_SoE_String;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。可在 System Manager 把 `ST_PlcDriveRef`（带 `AT %I*` 的过程映像）链接到 PLC，再用 `F_CreateAmsNetId` 把 NetID 字节数组转成字符串后逐字段填入（`sNetId` / `nSlaveAddr` / `nDriveNo` / `nDriveType`） |
| `bExecute` | `BOOL` | — | 上升沿触发一次写密码命令；调用期间保持，完成后手动复位 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间。`DEFAULT_ADS_TIMEOUT` 是 Tc2_System 的全局常量（典型 5 秒） |
| `sPassword` | `ST_SoE_String` | — | 以 Sercos 字符串形式给出的密码 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy        : BOOL;
    bError       : BOOL;
    iAdsErrId    : UINT;
    iSercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 被激活时置位，直到收到驱动器反馈才复位 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输出错则置位 |
| `iAdsErrId` | `UINT` | `bError` 置位时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError` 置位时返回上一条命令的 Sercos 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 是 `bExecute` 上升沿驱动的异步命令型功能块：

1. **触发**：`bExecute` 上升沿时，FB 把 `sPassword` 通过 SoE 写入到 `S-0-0267`，并置 `bBusy := TRUE`。
2. **执行中**：`bBusy` 保持 `TRUE`，FB 需被周期调用以推进内部 ADS 状态机直到驱动器回执；期间不要改输入。
3. **完成分支**：收到反馈后 `bBusy := FALSE`。传输无误则 `bError = FALSE`（密码已写入）；出错则 `bError := TRUE`，并在 `iAdsErrId` / `iSercosErrId` 给出错误码。

**寻址语义**：目标参数 `S-0-0267` 用 IDN 寻址（S = 标准参数集，编号 0267）。本 FB 内部已固定该 IDN，调用方只提供 `stDriveRef` 与 `sPassword`。

**使用时机**：密码是"解锁"动作的前置步骤——先用本 FB 写对密码，驱动器才允许后续对受保护 IDN 的写操作。密码写错不一定立即报错，可能是后续写参数时才返回"参数受保护"类 Sercos 错误。

**调用范式**：每周期调用实例推进状态机；`bBusy` 落下后补一次 `bExecute := FALSE` 调用收尾，便于下次重新触发。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bError = FALSE`（`bBusy` 已落） | 密码命令成功送达 | 可继续写受保护参数 |
| `bError = TRUE` | 命令传输出错 | 读 `iAdsErrId` / `iSercosErrId` |
| `iAdsErrId`（UINT） | ADS 通讯层错误码 | 参考 "ADS Return Codes" 表 |
| `iSercosErrId`（UINT） | 驱动器返回的 Sercos 错误码 | 参考驱动器型号的 Sercos 错误码手册 |

PDF 与 InfoSys 均未列出具体错误码表。ADS 码查通用 "ADS Return Codes"；Sercos 码查驱动器厂商诊断手册（⚠️ 待人工对照具体型号）。

## 5. 使用注意 / 常见坑

- **密码错误不一定当场报错**：写密码这一步可能成功（`bError = FALSE`），但口令值不对，要等到随后写受保护参数时驱动器才返回"参数受保护"类错误。排查时不要只看本 FB 的输出。（工程经验补充）
- **`sPassword` 是 Sercos 字符串类型 `ST_SoE_String`，不是普通 `STRING`**：直接把 `STRING` 字面量赋给它需注意类型，例程里用专门声明的 `ST_SoE_String` 变量传入。
- **密码不要硬编码进版本库**：源码里写死出厂密码有泄露风险，宜由 HMI 输入或受保护的配置区供给。（工程经验补充）
- **`stDriveRef` 必须先初始化好再触发**：`sNetId` 空或 `nSlaveAddr = 0` 时（上电初期过程映像未刷新）触发会指向错误目标，例程用 `bInit` 守卫。（工程经验补充）
- **`tTimeout` 用默认 `DEFAULT_ADS_TIMEOUT` 即可**：写密码是短命令，不像复位那样需要 10 秒。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEWritePassword_ByDriveRef.xml`](../examples/P_Demo_FB_SoEWritePassword_ByDriveRef.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEWritePassword_ByDriveRef
VAR
    fbWritePassword : FB_SoEWritePassword_ByDriveRef;
    rtrigWrite      : R_TRIG;
    stPlcDriveRef   AT %I* : ST_PlcDriveRef;
    stDriveRef      : ST_DriveRef;
    bInit           : BOOL := TRUE;
    bWriteReq       : BOOL := FALSE;                // 在线置 TRUE 触发写密码
    sDrivePassword  : ST_SoE_String;               // 在线填入实际口令
    bWriteBusy      : BOOL;
    bWriteError     : BOOL;
    iAdsErr         : UINT;
    iSercosErr      : UINT;
END_VAR

// 初始化驱动器引用
IF bInit THEN
    stDriveRef.sNetId     := F_CreateAmsNetId(stPlcDriveRef.aNetId);
    stDriveRef.nSlaveAddr := stPlcDriveRef.nSlaveAddr;
    stDriveRef.nDriveNo   := stPlcDriveRef.nDriveNo;
    stDriveRef.nDriveType := stPlcDriveRef.nDriveType;
    IF (stDriveRef.sNetId &lt;&gt; '') AND (stDriveRef.nSlaveAddr &lt;&gt; 0) THEN
        bInit := FALSE;
    END_IF;
END_IF;

rtrigWrite(CLK := bWriteReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值
fbWritePassword(
    stDriveRef := stDriveRef,
    bExecute   := rtrigWrite.Q AND NOT bInit,
    tTimeout   := DEFAULT_ADS_TIMEOUT,
    sPassword  := sDrivePassword,
    bBusy        => bWriteBusy,
    bError       => bWriteError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);

IF NOT bWriteBusy AND NOT bInit THEN
    bWriteReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：调试 AX5000 时需要修改受密码保护的厂商参数（如电机参数、调试限值），写入前必须先用 `S-0-0267` 解锁。把解锁动作做进 PLC，调试工程师在 HMI 输入密码即可，无需进 Drive Manager。
- **价值**：把"向 `S-0-0267` 写 Sercos 字符串 + 异步状态机 + 超时"封装成一次上升沿调用，密码值来源（HMI / 配置）与本 FB 解耦。
- **替代方案对比**：
  - 用 `FB_SoEWrite` 自己写 `S-0-0267`：要自己处理 IDN 与 Sercos 字符串编码
  - 在 Drive Manager 里手动输密码：只能调试时人工操作，不能在生产逻辑里自动化
  - **本 FB**：专为写密码封装，配合 HMI 口令输入即可在线解锁

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307543819.html
- **相关**：`FB_SoEReset_ByDriveRef`、`FB_SoEExecuteCommand_ByDriveRef`（同 General SoE 类）、`ST_SoE_String`（密码类型）

## 9. 待确认项

- ⚠️ `iAdsErrId` / `iSercosErrId` 取值表 PDF/InfoSys 均未列，需对照 ADS Return Codes 与具体驱动器 Sercos 错误码手册。
