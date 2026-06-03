# ConvertDcTimeToPos

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `Distributed Clocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57090443.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ConvertDcTimeToPos.TcPOU`](../examples/P_Demo_ConvertDcTimeToPos.TcPOU) |

---

## 1. 功能简述

把 32-bit Distributed Clock 系统时间（`T_DCTIME32`）转换为对应的 NC 轴位置。给定 DC 时间点，得到该时间点 NC 轴所在/将在的位置。是飞剪、印刷套准、电子凸轮等需要"时间-位置"双向映射场景的核心工具。

## 2. 接口定义

请参考 PDF §11.1.1 与 InfoSys topic 中描述的 VAR_INPUT / VAR_OUTPUT；本 FB 输入为目标 NC 轴引用与 DC 时间，输出为对应轴位置。

## 3. 行为说明

**触发**：调用即异步处理。本 FB 内部通过 NC 接口插值计算"给定时刻 NC 轴应到哪个位置"。常用于：
- 飞剪：根据上游编码器到达切割点的预测时间，计算 NC 切割轴在该时刻的目标位置
- 电子凸轮主从轴：根据主轴时间点预测从轴位置

**典型陷阱**：依赖 NC 轴 DC 同步配置正确；轴未在 OP 或 DC 不同步时返回值不可靠。任何对时间 - 位置映射精度敏感的应用，必须配合 `FB_EcExtSyncCheck64` 监测 DC 是否同步，并在 DC 失同步时立即抑制本 FB 计算结果不进入业务执行链路，避免错位剪切等严重事故。

## 4. 错误码 / 返回值

参考 PDF §11.1.1 与 InfoSys topic。

## 5. 使用注意 / 常见坑

- **DC 同步必须 OK**（工程经验补充）：先用 `FB_EcExtSyncCheck64` 确认 DC 同步
- **轴 OP**：轴未在 OP 状态时结果无意义
- **配 ConvertPosToDcTime 配对使用**：互为逆运算

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ConvertDcTimeToPos.TcPOU`](../examples/P_Demo_ConvertDcTimeToPos.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：飞剪应用，上游编码器输出"产品 0.5 秒后到切割点"，PLC 调本 FB 计算 0.5 秒后切割轴应在的位置，提前发位置指令
- **价值**：把"时间预测"转化为"位置预测"，让飞剪同步精确
- **替代方案对比**：手算预测 → 易错；本 FB → NC 接口标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §11.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57090443.html
- **相关 FB / FC**：`ConvertPosToDcTime`（逆运算）、`ConvertDcTimeToPathPos`（路径距离）、`T_DCTIME32`
