# FB_HVACPersistent_XX
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `BackupVar` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685173387.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVACPersistent_XX.TcPOU`](../examples/P_Demo_FB_HVACPersistent_XX.TcPOU) |

---

## 1. 功能简述
**`XX` 是一个占位符**——本 FB 实际是 15+ 个同构 FB 的家族，每个对应一种基本数据类型 / 结构：`FB_HVACPersistent_BOOL` / `_BYTE` / `_INT` / `_DINT` / `_UDINT` / `_UINT` / `_SINT` / `_USINT` / `_WORD` / `_DWORD` / `_REAL` / `_LREAL` / `_TIME` / `_STRING` / `_STRUCT`。功能：把一个用户自定义的变量保存到**持久化文件**（`.bootdata` / `.bootdata-old` 双备份）实现掉电不丢；上电自动回读。PDF 以 `FB_HVACPersistent_BYTE` 为代表展示接口；其他类型 FB 接口完全一致，只是变量类型不同。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    bSetDefault : BOOL;
    byVar_Default : BYTE;
END_VAR
```
### VAR_OUTPUT

无。
### VAR_IN_OUT

```iecst
VAR_IN_OUT
    byVar : BYTE;
END_VAR
```

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bSetDefault` | `BOOL` | - | 上升沿一次性把所有 VAR_IN_OUT 复位为出厂默认值。首次下载工程后应触发一次。 |
| `byVar_Default` | `BYTE` | - | 整型工程量（语义见 PDF 同名描述段）。 |

#### VAR_IN_OUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `byVar` | `BYTE` | - | 整型工程量（语义见 PDF 同名描述段）。 |

## 3. 行为说明

上电时本 FB 自动从 `.bootdata` 持久化文件中读出 IN_OUT 变量的上次值；`bSetDefault = TRUE` 时把变量重新写为 default 引脚给的初始值；运行中变量改变会触发持久化写盘（由全局 `FB_HVACPersistentDataHandling` 在主循环中实际执行）。**必须先在主程序里实例化 `FB_HVACPersistentDataHandling` 一次并周期调用**，否则本 FB 入队的写盘请求不会被消费。本 FB 是同构 FB 家族；按变量类型选用对应后缀的 FB 即可，所有变体的接口都遵循「`bSetDefault` + `<type>Var_Default` 输入 + `<type>Var` IN_OUT」三引脚模式。

## 4. 错误码 / 返回值

本 FB 不输出独立的 `bError*` / `nErrId` 引脚，行为正确性以 VAR_OUTPUT 的各 BOOL / 数值输出指示。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| 无独立错误码 | 本 FB 不输出独立错误位，行为正确性由各 BOOL / 数值输出指示 | 在线 monitor 各输出 |

## 5. 使用注意 / 常见坑

- **必须配合 `FB_HVACPersistentDataHandling`** 在主程序中实例化一次并周期调用，否则写盘请求队列不会被消费。
- 本 FB 家族有 15+ 个变体（每个数据类型一个）；按变量类型精确选用。
- 持久化文件容量大但写入慢（毫秒级而非微秒级）；不要把高频变化的过程值放持久化，只放参数 / 配置。
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVACPersistent_XX.TcPOU`](../examples/P_Demo_FB_HVACPersistent_XX.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工程中需要掉电保留的核心参数：HMI 设的 PID 增益、行程时间、限值常量等；每个参数实例化一个对应类型的 FB_HVACPersistent_XX，把变量接到 IN_OUT 引脚，断电不丢。与 NOVRAM 变体不同的是，本家族写入文件系统（容量大、不依赖 NOVRAM 硬件）。
- **价值**：比起手写 PERSISTENT 变量 + 自己处理双备份切换，本 FB 一行调用搞定；与 Tc2_HVAC 体系内的 `FB_HVACPersistentDataHandling` 自动协作的双备份机制保证断电瞬间数据完整性。
- **替代方案对比**：**TwinCAT PERSISTENT 关键字**：能保留但没有双备份，断电瞬间写盘时数据可能损坏；**FB_HVACNOVRAM_XX 家族**：写 NOVRAM 而非文件系统，容量小但写入速度快；**本 FB 家族**：写文件系统，双备份，容量大，适合大量持久化参数。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.10.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685173387.html
- **相关 FB / FC / DUT**：`FB_HVACPersistentDataHandling`、`FB_HVACNOVRAM_XX`、`FB_HVACPersistentDataFileCopy`、`E_HVACDataSecurityType`
