# Get_TcNcCfg_Version

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3438162827.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_Get_TcNcCfg_Version.TcPOU`](../examples/P_Demo_Get_TcNcCfg_Version.TcPOU) |

---

## 1. 功能简述

`Get_TcNcCfg_Version` 返回旧版 `TcNcCfg.lib`（TwinCAT 2 PLC 库）版本号字符串，仅为旧项目兼容保留。新项目应改用 `stLibVersion_Tc2_NCI` 全局常量。

## 2. 接口定义

### VAR_INPUT

无（本 POU 无 `VAR_INPUT` 参数）。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 返回值（FUNCTION）

| 名称 | 类型 | 说明 |
|---|---|---|
| `Get_TcNcCfg_Version` | `STRING(20)` | 旧 `TcNcCfg.lib`（TwinCAT 2 PLC 库）版本号字符串（如 `'1.2.3'`） |

## 3. 行为说明

**用法**：调用 `Get_TcNcCfg_Version(bGet := TRUE)`，返回旧 `TcNcCfg.lib`（TwinCAT 2 NC 配置 PLC 库）版本号字符串（如 `'1.2.3'`）。

**实现**：纯 FC，不走 ADS、不读 cyclic interface、无副作用。返回值由 PLC 编译期把库链接信息直接嵌进二进制——所以运行时即时返回，零开销。

**新项目应替换**：本 FC 仅给 TwinCAT 2 移植项目用。新项目应直接读 `stLibVersion_Tc2_NCI` 全局常量、配 `F_CmpLibVersion` 做版本检查。TwinCAT 3 已无独立的『NcCfg』库，所有 NC 配置 PLC API 都合并进了 `Tc2_NCI`。

## 4. 错误码 / 返回值

`Get_TcNcCfg_Version` 是纯函数（FC），不通过 `bErr` / `nErrId` 输出错误：调用即返回，返回值直接给到 `Get_TcNcCfg_Version` 调用表达式。如果 cyclic channel interface 配置不对（如 `sNciToPlc` 没 Link 给 NC），返回值会读到 0 或异常值——这种『静默失败』在 PLC 端难直接定位，建议把 `ItpHasError(sNciToPlc)` 与 `ItpGetError(sNciToPlc)` 配合做通道级错误轮询。

## 5. 使用注意 / 常见坑

- 见 §3 行为说明列出的『典型陷阱』段。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Get_TcNcCfg_Version.TcPOU`](../examples/P_Demo_Get_TcNcCfg_Version.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// FUNCTION 调用——返回值直接赋给本地变量观察
Get_TcNcCfg_Version_ret := Get_TcNcCfg_Version();

```

## 7. 业务场景与实际价值

- **场景**：仅为读取旧版 TwinCAT 2 PLC 库（`TcNciUtilities.lib` / `TcNcCfg.lib` / `TcNC.lib`）版本号保留。
- **价值**：旧项目兼容。
- **替代方案对比**：新项目使用 `stLibVersion_Tc2_NCI` 全局常量配 `Tc2_System.F_CmpLibVersion`。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3438162827.html
- **相关 FB / FC**：见 §3 行为说明

