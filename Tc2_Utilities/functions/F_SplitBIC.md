# F_SplitBIC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11533409675.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SplitBIC.xml`](../examples/P_Demo_F_SplitBIC.xml) |

---

## 1. 功能简述

把 Beckhoff Identification Code (BIC) 按各段标识符（`1P`、`SBTN`、`1K`、`Q`、`2P` 等）拆分成 `ST_SplittedBIC` 结构体并返回。

BIC 是多段拼接的标识：`1P`=物料号、`SBTN`=追溯号、`1K`=订单号、`Q`=设备代码、`2P`=序列号。一次调用即可拿到所有已知字段，未识别的尾段被放进 `sUndefined` 字段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sBICValue   : STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sBICValue` | `STRING` | — | 完整的 Beckhoff Identification Code (BIC) 字符串。例：`'1P193995SBTN0002agdw1KEL7411 Q1 2P112104020018'`。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `ST_SplittedBIC` | 结构化的拆分结果（`ST_SplittedBIC`，包含物料号、BTN、订单号、序列号、自定义号、设备代码、未识别段等字段）；未出现的子段为空串。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回，无状态。函数内部按已知标识符 (`1P` / `SBTN` / `1K` / `Q` / `2P` 等) 顺序扫描 `sBICValue`，把每个标识后跟随的子串截取并填入结构体对应字段；每个子串末尾空格自动去除；未出现的标识对应字段保持为空串。如果遇到**未知**标识，剩余整段 BIC 被原样放入 `sUndefined` 字段，便于上层日志诊断。

**与 `BIC_TO_BTN` 的差别**：`BIC_TO_BTN` 只回单一 BTN 子段；`F_SplitBIC` 一次性拆出所有字段，适合做完整 MES 上报。

## 4. 错误码 / 返回值

返回 `ST_SplittedBIC` 结构，无单独错误码。判断成功的方式：检查 `sUndefined` 是否为空——非空表示 BIC 中含未知段、解析不完全。

## 5. 使用注意 / 常见坑

- **未知字段进 sUndefined**：检查 `LEN(stOut.sUndefined) > 0` 即「BIC 含未识别段」，应记日志。
- **未出现的标识对应字段为空**：例如 BIC 没有 `Q` 段时 `stOut.sDeviceCode = ''`，业务侧用空判别。
- **BIC 来源**：用 `FB_EcCoEReadBIC` / `FB_EcReadBIC`（`Tc2_EtherCAT`）从从站读出。
- **比逐字段调用更高效**：避免对同一 BIC 反复 `BIC_TO_BTN` + 自写 `1P` / `1K` 提取——一次 `F_SplitBIC` 解决。
- **结构体字段名见 `ST_SplittedBIC` 文档**（PDF §5）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitBIC.xml`](../examples/P_Demo_F_SplitBIC.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_SplitBIC
VAR
    sBicRaw   : STRING := '1P193995SBTN0002agdw1KEL7411 Q1 2P112104020018';
    stSplit   : ST_SplittedBIC;   // 在线展开看每个字段（在线 monitor）
END_VAR

// 单行调用：一次拆出所有字段
stSplit := F_SplitBIC(sBicRaw);

```

## 7. 业务场景与实际价值

- **场景**：MES 完整追溯——除 BTN 外还要记录物料号、订单号、序列号、设备代码。一次解析填入数据库一行记录。
- **价值**：减少多次字符串扫描的代码量与 CPU 开销；结构化字段便于直接 `INSERT INTO`。
- **替代方案对比**：
  - 多次调用 `BIC_TO_BTN` 等：每次都全串扫描一遍，浪费
  - 手写状态机扫描：30 行以上，易在边界（空段、未知段）出错
  - **本函数**：单调用、PDF 给出 BIC 完整示例

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.40 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11533409675.html
- **相关函数**：`BIC_TO_BTN`（仅取 BTN）、`ST_SplittedBIC`（返回结构体定义）、`FB_EcCoEReadBIC` / `FB_EcReadBIC`（`Tc2_EtherCAT`）
