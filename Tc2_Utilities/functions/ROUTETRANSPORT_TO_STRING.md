# ROUTETRANSPORT_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35149835.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_ROUTETRANSPORT_TO_STRING.TcPOU`](../examples/P_Demo_ROUTETRANSPORT_TO_STRING.TcPOU) |

---

## 1. 功能简述

把 AMS 消息路由的传输层枚举（`E_RouteTransportType`）转为可读字符串，便于日志诊断。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eType : E_RouteTransportType;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `eType` | `E_RouteTransportType` | — | 传输层标识枚举（`E_RouteTransportType`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：根据 `eType` 枚举值查内部映射表返回对应的可读字符串：`'TCP/IP'`、`'NetBIOS'`、`'UDP'`、`'COM'` 等（具体取值范围见 `E_RouteTransportType` 文档）。**只用于诊断 / 日志展示**——不参与业务逻辑判断，业务侧用枚举值本身（不要把字符串再 `STRING_TO_ENUM`，IEC 没这种通用函数）。通常配合 `FB_GetRouteListEntry` 等 ADS 路由查询 FB 使用：先用 FB 拿到路由表条目（含 `E_RouteTransportType` 字段），再用本函数渲染到 HMI / 日志。未知枚举值的返回 ⚠️ PDF/InfoSys 未明示，建议只传合法枚举常量。

## 4. 错误码 / 返回值

返回 `STRING`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **只用于显示 / 日志**——不要把返回值再 `STRING_TO_ENUM` 反向解析（IEC 没这种函数）。
- **`E_RouteTransportType` 枚举值需查 PDF / InfoSys 类型文档**。
- 返回类型 `STRING`——具体长度按枚举名称定。
- **通常与 `FB_GetRouteListEntry` 等 ADS 路由查询 FB 配合**。
- 未知枚举值的返回 ⚠️ PDF 未明示，建议传合法值。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ROUTETRANSPORT_TO_STRING.TcPOU`](../examples/P_Demo_ROUTETRANSPORT_TO_STRING.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 显示 ADS 路由表：每行路由的传输层标识用本函数转为可读字符串。
- **价值**：替代手写枚举 → 字符串 switch 表；统一与 Beckhoff 工具的命名风格。
- **替代方案对比**：**无替代**——这是 Beckhoff 内部枚举的官方字符串映射。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.65 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35149835.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
