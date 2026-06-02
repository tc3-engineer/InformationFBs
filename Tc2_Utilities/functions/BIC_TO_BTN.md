# BIC_TO_BTN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11533405835.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_BIC_TO_BTN.TcPOU`](../examples/P_Demo_BIC_TO_BTN.TcPOU) |

---

## 1. 功能简述

从 Beckhoff Identification Code (BIC) 字符串中**抽取 Beckhoff Traceability Number (BTN, 追溯编号)** 并以 `STRING(9)` 返回。

BIC 是 Beckhoff EtherCAT 从站 / 模块的统一标识，含多段子标识符（`1P` 物料号、`SBTN` 追溯号、`1K` 订单号、`2P` 序列号等）。本函数仅取出 `SBTN` 标识后跟随的 8 位 BTN 子串，便于程序读取并存入产品追溯日志。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sBICValue   : STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sBICValue` | `STRING` | — | 包含 Beckhoff Identification Code (BIC) 的字符串。函数从中提取 BTN 子串。例：`'1P193995SBTN0002agdw1KEL7411 Q1 2P112104020018'` 会返回 `'0002agdw'`。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(9)` | Beckhoff Traceability Number (BTN) 子串；末尾空格自动去除；若 BIC 中未找到 BTN 标识则返回空串 `''`。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回，无内部状态。在 `sBICValue` 中查找子串 `'SBTN'`，从其后开始取 8 个字符作为 BTN；末尾空格自动 trim。若字符串中找不到 `'SBTN'` 标识则返回 `''`。**返回类型固定为 `STRING(9)`**——容纳 8 位 BTN + 终止符。

BTN 由字母 + 数字混合，本函数不做格式校验：只要找到 `SBTN` 子串即按位置截取，调用方需自己再做合法性检查。

## 4. 错误码 / 返回值

返回 `STRING(9)`，无错误码、无 `bError`。**返回空串 `''` 即表示未找到**——业务侧用 `LEN(sBtn) = 0` 判定。

## 5. 使用注意 / 常见坑

- **找不到时返回空串**：业务侧必须先 `IF LEN(sBtn) > 0 THEN ...` 再用，否则会把空串当真 BTN 写日志。
- **不做格式校验**：返回值可能含 `\x00` 之类异常字符（取决于 BIC 是否完整）；写日志前用 `F_RTrim` 过滤。
- **配套 F_SplitBIC**：若同时需要其他子标识（物料号、订单号），调用 `F_SplitBIC` 一次性拿到结构化结果，比多次 `BIC_TO_BTN` 类调用更省。
- **BIC 来源**：通常用 `FB_EcCoEReadBIC` / `FB_EcReadBIC`（`Tc2_EtherCAT` 库）从 EtherCAT 从站读出原始 BIC 字符串，再喂给本函数。
- **不能反推**：BTN 唯一，但 BIC 含多个子段；本函数只取 BTN，不可用来反推 BIC 其他段。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BIC_TO_BTN.TcPOU`](../examples/P_Demo_BIC_TO_BTN.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BIC_TO_BTN
VAR
    sBicRaw : STRING := '1P193995SBTN0002agdw1KEL7411 Q1 2P112104020018';
    sBtn    : STRING(9);     // 提取出的 BTN（在线 monitor）
END_VAR

// 单行调用：从 EtherCAT 从站读到的 BIC 抽出追溯号
sBtn := BIC_TO_BTN(sBicRaw);

```

## 7. 业务场景与实际价值

- **场景**：产线产品追溯——MES 要求记录每台机器上每个 EtherCAT 从站的 BTN（出厂追溯号），便于 RMA / 维修时定位生产批次。从 `FB_EcCoEReadBIC` 读到的 BIC 经本函数提取 BTN 后写入数据库。
- **价值**：避免手写字符串扫描 `FIND('SBTN', ...) + MID(...)` 三步，一行调用；BTN 长度固定 8 位，本函数封装了长度常量。
- **替代方案对比**：
  - 手写 `FIND + MID + RTrim`：3 行 + 边界判断，易在「找不到 SBTN」时漏 `LEN=0` 检查
  - `F_SplitBIC`：可一次拿到 BTN 和其他字段，**若只要 BTN 用本函数更省**
  - **本函数**：单一职责、PDF 双源确认

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.13 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11533405835.html
- **相关函数**：`F_SplitBIC`（拆分整个 BIC）、`FB_EcCoEReadBIC` / `FB_EcReadBIC`（`Tc2_EtherCAT`，读取原始 BIC）
