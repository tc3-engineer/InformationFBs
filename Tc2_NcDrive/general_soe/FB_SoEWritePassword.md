# FB_SoEWritePassword

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NcDrive` |
| Library Version | `1.2.9` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305001099.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEWritePassword.xml`](../examples/P_Demo_FB_SoEWritePassword.xml) |

---

## 1. 功能简述

向伺服驱动器写入**密码**的功能块（Function Block, FB），对应 SoE 参数 S-0-0267。把口令作为 Sercos 字符串（`ST_SoE_String`）传入，`bExecute` 上升沿触发后通过 SoE 通道写到驱动器，用于解锁那些受密码保护、否则无法修改的驱动器参数。

轴定位同样通过 `NCTOPLC_AXIS_REF` 轴引用完成，不需要单独指定驱动器地址。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId    : T_AmsNetId := '';
    bExecute  : BOOL;
    tTimeout  : TIME := DEFAULT_ADS_TIMEOUT;
    sPassword : ST_SoE_String;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | `''` | 目标控制器（IPC）的 AMS Network ID 字符串；空串 `''` 表示本机 |
| `bExecute` | `BOOL` | — | 上升沿启动一次写密码命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间 |
| `sPassword` | `ST_SoE_String` | — | 以 Sercos 字符串形式给出的驱动器密码 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : NCTOPLC_AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `NCTOPLC_AXIS_REF` | NC 轴数据结构（映射在 `%I*` 输入过程映像）；本 FB 据此定位目标驱动器 |

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
| `bBusy` | `BOOL` | 命令激活后置 `TRUE`，直到收到反馈才复位；期间不接受新命令 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输发生错误则置 `TRUE` |
| `iAdsErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发与时序**：`bExecute` 上升沿启动写密码，`bBusy` 立即置 `TRUE`，FB 把 `sPassword` 内容作为 Sercos 字符串写入 S-0-0267。收到驱动器反馈后 `bBusy` 复位；若传输出错，`bBusy` 落下之后 `bError` 置 `TRUE`，并由 `iAdsErrId` / `iSercosErrId` 给出错误码。标准用法是触发后在 `NOT bBusy` 时把 `bExecute` 写回 `FALSE` 复位边沿。

**密码格式**：`sPassword` 是 `ST_SoE_String` 类型的 Sercos 字符串，内容由驱动器手册规定（不同驱动器密码不同）。写入正确密码后，该驱动器中受保护的参数才可被后续 `FB_SoEWrite` 修改。

**作用范围**：本 FB 只负责把密码送到驱动器，不验证密码正确与否的细节由驱动器决定；若密码不被接受，驱动器会返回 Sercos 错误码，从 `iSercosErrId` 读出。

## 4. 错误码 / 返回值

本 FB 无函数返回值，错误通过 `bError = TRUE` 配合两个错误码输出表达：

| 输出 | 类型 | 含义 |
|---|---|---|
| `iAdsErrId` | `UINT` | ADS 传输层错误码（命令下发链路问题） |
| `iSercosErrId` | `UINT` | Sercos / SoE 协议层错误码（驱动器拒绝写 S-0-0267，如密码格式/权限问题时返回） |

⚠️ PDF 与 InfoSys 在本 FB 章节均未逐条列出具体数值含义。ADS 错误码见 Beckhoff 通用 ADS Return Codes 主题；Sercos 错误码以对应驱动器手册为准。

## 5. 使用注意 / 常见坑

- **密码内容来自驱动器手册**：不同型号驱动器密码不同，别套用别的设备密码。
- **写密码 ≠ 改参数**：本 FB 只是解锁，解锁后还要用 `FB_SoEWrite` 写具体的受保护参数。
- **边沿触发，需手动复位 `bExecute`**：`bBusy` 落下后把 `bExecute` 写 `FALSE` 才能触发下一次。
- **密码写错看 `iSercosErrId`**：驱动器拒绝时错误从 Sercos 一路返回，不是 ADS 路。
- **`Axis` 是 VAR_IN_OUT 必须传引用**：传入映射在 `%I*` 上的 `NCTOPLC_AXIS_REF` 实例。
- **`sPassword` 不要硬编码在公开代码里**：工程经验补充，敏感口令建议从受控配置注入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEWritePassword.xml`](../examples/P_Demo_FB_SoEWritePassword.xml)

```iecst
// 场景：调试 AX5000 需要修改受密码保护的电机参数，先写入驱动器密码解锁
PROGRAM P_Demo_FB_SoEWritePassword
VAR
    fbWritePassword   : FB_SoEWritePassword;
    NcToPlcAxis AT %I*: NCTOPLC_AXIS_REF;
    sDrivePassword    : ST_SoE_String;        // 由驱动器手册给出的口令
    bUnlockRequest    : BOOL;
    rtUnlock          : R_TRIG;
    bBusy             : BOOL;
    bError            : BOOL;
    iAdsErr           : UINT;
    iSercosErr        : UINT;
END_VAR

rtUnlock(CLK := bUnlockRequest);
fbWritePassword(
    Axis      := NcToPlcAxis,
    sNetId    := '',
    bExecute  := rtUnlock.Q,
    tTimeout  := DEFAULT_ADS_TIMEOUT,
    sPassword := sDrivePassword,
    bBusy        => bBusy,
    bError       => bError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);
IF NOT bBusy THEN
    bUnlockRequest := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：调试或售后维护时需修改 AX5000 等驱动器中受密码保护的参数（如电机铭牌、换向角），在写参数前用本 FB 解锁。
- **价值**：不用本 FB 时要自己用 `FB_SoEWrite` 操作 S-0-0267 并处理 Sercos 字符串编码与时序；本 FB 把"解锁"动作封装成一个带错误码反馈的 `bExecute` 边沿。
- **替代方案对比**：
  - 用 `FB_SoEWrite` 直接写 S-0-0267：通用但要自己拼 Sercos 字符串、管时序
  - **本 FB**：写驱动器密码的专用封装，语义清晰

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf) §3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305001099.html
- **相关 FB**：`FB_SoEWrite`（写受保护参数）、`FB_SoEReset`（复位驱动器）
