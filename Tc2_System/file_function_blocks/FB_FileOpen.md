# FB_FileOpen

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30977547.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileOpen.xml`](../examples/P_Demo_FB_FileOpen.xml) |

---

## 1. 功能简述

FB_FileOpen 通过 ADS 异步打开或新建一个文件，并返回文件句柄 `hFile`。`hFile` 是后续 `FB_FileRead` / `FB_FileWrite` / `FB_FileGets` / `FB_FilePuts` / `FB_FileSeek` / `FB_FileTell` / `FB_FileClose` 操作的唯一入口标识。本 FB 必须周期调用，状态机走完 `bExecute` 上升沿 → `bBusy = TRUE` → `bBusy = FALSE` 且 `bError = FALSE` 才算成功，得到的 `hFile` 不为 0。

**适用范围限制**：PDF 明确指出本 FB 不适合实时高频日志写入（每周期写一条会撑爆 ADS 队列），高吞吐量日志应改用 TF3500 TwinCAT Analytics Logger 这一付费产品。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sPathName : T_MaxString;
    nMode : DWORD;
    ePath : E_OpenPath := PATH_GENERIC;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `sPathName` | `T_MaxString` | - | 要打开 / 新建的文件路径（绝对或相对于 `ePath` 基准）。**只能本地路径**，不支持 UNC / 网络路径。 |
| `nMode` | `DWORD` | - | 打开模式位掩码（`FOPEN_MODEREAD` / `FOPEN_MODEWRITE` / `FOPEN_MODEAPPEND` / `FOPEN_MODEPLUS` / `FOPEN_MODEBINARY` / `FOPEN_MODETEXT`，可 OR 组合）。 |
| `ePath` | `E_OpenPath` | `PATH_GENERIC` | TwinCAT 系统路径基准枚举（如 `PATH_GENERIC` / `PATH_BOOTPATH` / `PATH_GENERIC_USERDATA`）。默认 `PATH_GENERIC`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    hFile : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |
| `hFile` | `UINT` | **输出参数**：打开成功后的文件句柄，传给后续 `FB_FileRead` / `FB_FileWrite` / `FB_FileClose`。`bError = TRUE` 时通常为 0，不可使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：本 FB 是异步 ADS 调用包装，必须每个 PLC 周期调用一次直到 `bBusy` 复位为 FALSE。`bExecute` 上升沿后，`bBusy` 立刻置 TRUE 并启动一次 ADS 请求；ADS 应答返回后 `bBusy` 复位，`bError` 与 `nErrId` 给出结果，成功时 `hFile` 装载新句柄。

**`nMode` 模式位掩码**（可以 OR 组合，类似 C 语言的 `fopen`）：

- `FOPEN_MODEREAD`（r）：只读打开，文件必须存在，否则报错。
- `FOPEN_MODEWRITE`（w）：只写打开，文件存在则被截断；不存在则新建。
- `FOPEN_MODEAPPEND`（a）：追加写打开，写指针始终在末尾；不存在则新建。
- `OR FOPEN_MODEPLUS`（+）：与 r / w / a 组合，得到读 + 写模式（r+ / w+ / a+）。`a+` 必须指定有效存储路径，否则报错 1804。
- `FOPEN_MODEBINARY`（b） / `FOPEN_MODETEXT`（t）：二进制模式 / 文本模式。二进制按字节原样读写；文本模式在 Windows 上做 CR/LF ↔ LF 自动转换。

**`ePath` 路径基准**：决定 `sPathName` 是绝对路径还是相对于某个 TwinCAT 系统路径。常用值：`PATH_GENERIC` 通用绝对路径、`PATH_BOOTPATH` TwinCAT Boot 目录、`PATH_GENERIC_USERDATA` 用户数据目录、`PATH_USERPATH1..4` 自定义路径。默认 `PATH_GENERIC`。

**`hFile = 0` 的语义**：当 `bError = TRUE` 时 `hFile` 通常为 0，**不可**作为合法句柄传给后续读写。

**`a+` 路径要求**：以 `FOPEN_MODEAPPEND OR FOPEN_MODEPLUS` 打开新文件时，PDF 明确指出必须能解析出有效路径，否则返回错误号 1804。

**追加模式细节**：`a` / `a+` 模式下所有写操作都强制在文件末尾进行，`FB_FileSeek` 不能改变写位置（读位置可改）。

## 4. 错误码 / 返回值

本 FB 通过 `bError` + `nErrId` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`（**ADS Return Codes**）。

常见错误号（部分）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x70C` | 文件不存在 / 路径无效（ADSERR_DEVICE_NOTFOUND_FILE） |
| `0x70D` | 文件已存在（创建模式时） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| `0x1804` | 路径错误（FOPEN_MODEAPPEND 时常见，需路径已知） |
| 其他 | 见 Beckhoff ADS Return Codes 在线表 |

## 5. 使用注意 / 常见坑

- **路径只能本地**：`sNetId` 即使填了远端 NetID，路径仍是『目标 PC 的本地路径』，不支持 UNC `\\server\share\...` 网络路径，PDF 明确指出。
- **`hFile` 必须 `FB_FileClose`**：打开后未关闭会导致目标 PC 上文件句柄泄漏，长时间运行可能耗尽系统句柄；建议用结构化状态机或 `FB_FileLoad` / `FB_FileSave` 风格的封装。
- **`a+` 模式必须能解析路径**：相对路径 + `PATH_GENERIC` 经常报 1804；切到 `PATH_GENERIC_USERDATA` 或填绝对路径解决。
- **`tTimeout` 默认 5 秒太短**：大文件 / 远程网络 / 慢 SD 卡场景下 5 秒可能不够，建议至少 30 秒；写 100MB 以上文件用 60+ 秒。（工程经验补充）
- **实时性陷阱**：每个 PLC 周期开一次文件并不会让 `hFile` 更早返回，反而把 ADS 队列堵满。建议把 `FB_FileOpen` 放在状态机的 `INIT` 步而不是 `MAIN` 循环。（工程经验补充）
- **线程独占**：同一文件不要在多个任务里同时打开同一句柄；多个 FB_FileOpen 实例同时打开同一文件可能拿到不同句柄但底层文件锁冲突。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileOpen.xml`](../examples/P_Demo_FB_FileOpen.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：设备启动时打开一份配方 INI 文件准备读取，或在班次切换时新建一个 CSV 日志文件继续追加运行参数。
- **价值**：不用本 FB 时必须自己组装 ADS Write 命令（IndexGroup `0x10005` / IndexOffset 不同模式）并手动 wrap busy / done 状态机，约 40 行代码。本 FB 封装好了这套时序。
- **替代方案对比**：
  - 直接调用 `ADSWRITE` / `ADSREAD` 操控文件 ADS 接口：能用但要自己跟踪 IndexGroup 与状态机，错一字节就挂。
  - TF3500 Analytics Logger：付费插件，性能远超本 FB，适合高吞吐日志。
  - `FB_FileLoad` / `FB_FilePuts` 一次性 API：场景固定（整文件读 / 单行写）时更简洁，但灵活性差。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30977547.html
- **相关 FB / FC**：`FB_FileClose`, `FB_FileRead`, `FB_FileWrite`, `FB_FileGets`, `FB_FilePuts`, `FB_FileLoad`, `FB_FileSeek`, `FB_FileTell`, `FB_FileDelete`
