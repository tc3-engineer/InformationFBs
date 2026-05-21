# Constants

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `VAR_GLOBAL` |
| Category | `Global constants` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/18014398540566155.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_Constants.xml`](../examples/P_Demo_Constants.xml) |

---

## 1. 功能简述

Tc2_System 库提供一组全局常量集中定义在 `Constants`（章节 6.1）中，覆盖 ADS 端口号、ADS 状态码、ADS 索引组、文件打开模式等多类常量。应用代码不要硬编码这些数字，应直接引用对应的常量符号，提升可读性并避免维护时数字写错。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**常量分组**：

**1. ADS 端口号（`AMSPORT_*`）**：标识 TwinCAT 各服务的端口。常用：

- `AMSPORT_R0_PLC_RTS1` = 801 （TwinCAT 2.x PLC Runtime 1，老版兼容）
- `AMSPORT_R0_PLC_TC3` = 851 （TwinCAT 3 PLC Runtime，新版默认）
- `AMSPORT_R0_NC` = 500 （NC Server）
- `AMSPORT_R0_IO` = 300 （IO Server）
- `AMSPORT_LOGGER` = 100 （日志服务器）
- `AMSPORT_R3_SYSSERV` = 10000 （System Service）

**2. ADS 状态码（`ADSSTATE_*`）**：标识 ADS 对象当前状态：`ADSSTATE_RUN` = 5、`ADSSTATE_STOP` = 6、`ADSSTATE_CONFIG` = 15、`ADSSTATE_RECONFIG` = 16 等。

**3. ADS 索引组（`ADSIGRP_*`）**：标识 ADS 数据访问的索引组：`ADSIGRP_SYMTAB` = `16#F000`、`ADSIGRP_SYM_INFOBYNAME` 等。

**4. 其他**：文件打开模式（`FOPEN_MODE*`）、Default ADS 超时（`DEFAULT_ADS_TIMEOUT`）等。

**全部常量见 PDF §6.1**。本节列出最常用的；完整列表逐条搬运过来意义不大，建议查 PDF 或 InfoSys 对应章节。

## 4. 错误码 / 返回值

本节是 `VAR_GLOBAL CONSTANT` 集合，无返回值。

**核心常量速查**：

| 常量名 | 值 | 说明 |
|---|---|---|
| `AMSPORT_R0_PLC_TC3` | 851 | TwinCAT 3 PLC Runtime 默认端口 |
| `AMSPORT_R0_PLC_RTS1` | 801 | TwinCAT 2 PLC Runtime 1（兼容） |
| `AMSPORT_R0_NC` | 500 | NC Server |
| `AMSPORT_LOGGER` | 100 | 日志服务器 |
| `ADSSTATE_RUN` | 5 | ADS 对象运行中 |
| `ADSSTATE_STOP` | 6 | ADS 对象停止 |
| `ADSSTATE_CONFIG` | 15 | TwinCAT 配置模式 |
| `DEFAULT_ADS_TIMEOUT` | T#5S | 默认 ADS 调用超时 |
| `FOPEN_MODEREAD` | 1 | 只读 |
| `FOPEN_MODEWRITE` | 2 | 只写 |
| `FOPEN_MODEAPPEND` | 4 | 追加 |
| `FOPEN_MODEPLUS` | 16 | 读写 |
| `FOPEN_MODEBINARY` | 32 | 二进制模式 |
| `FOPEN_MODETEXT` | 64 | 文本模式 |

## 5. 使用注意 / 常见坑

- **不要硬编码数字**：写 `nPort := 801` 不如 `nPort := AMSPORT_R0_PLC_RTS1` 直观；后续维护看到 851 还是 801 一目了然。
- **TwinCAT 2 vs 3 PLC 端口**：851 是 TC3 默认，老工程的 801 / 811 是 TC2，跨版本通讯要核对。
- **常量值不可改**：`VAR_GLOBAL CONSTANT` 编译期定下，运行期赋值会报错。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Constants.xml`](../examples/P_Demo_Constants.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MAIN 中调用 ADSREAD 时用 `nPort := AMSPORT_R0_PLC_TC3` 而不是硬编码 851；新人接手代码也能立刻明白这是 TC3 的 PLC 端口。
- **价值**：替代魔法数字；可读性大幅提升。
- **替代方案对比**：
  - 自定义常量：可行但重复造轮子。
  - 硬编码：可维护性最差。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/18014398540566155.html
- **相关 FB / FC**：`stLibVersion_Tc2_System`, `FB_FileOpen`, `F_CmpLibVersion`
