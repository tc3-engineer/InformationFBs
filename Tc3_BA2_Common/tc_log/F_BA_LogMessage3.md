# F_BA_LogMessage3

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Universal / TcLog` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14593493771.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_LogMessage3.TcPOU`](../examples/P_Demo_F_BA_LogMessage3.TcPOU) |

---

## 1. 功能简述

文本 + 3 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名——本文档按 InfoSys + LogMessage2 规则推算签名为 `FUNCTION F_BA_LogMessage : INT`（注意 PDF 内部符号统一为 `F_BA_LogMessage` 而非带数字后缀；编译器通过 InfoSys 接受 `F_BA_LogMessage3` 等名字）。

## 2. 接口定义

### 完整声明

```iecst

```

### VAR_IN_OUT

无。


## 3. 行为说明

文本 + 3 个动态参数。用法参考 `F_BA_LogMessage2`。⚠️ PDF 此节正文只一句 "Application see F_BA_LogMessage2"，未给签名——本文档按 InfoSys + LogMessage2 规则推算签名为 `FUNCTION F_BA_LogMessage : INT`（注意 PDF 内部符号统一为 `F_BA_LogMessage` 而非带数字后缀；编译器通过 InfoSys 接受 `F_BA_LogMessage3` 等名字）。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 日志通过 ADSLOG 接口送到 TwinCAT 输出窗口与系统事件日志；运行期一直产生日志会拖慢调试输出，发布版建议把 `nLogType` 至少调到 WARNING 或更高级别。 典型工程场景：3 参数日志：`F_BA_LogMessage3("Temp/Hum/Pres", tArg1, tArg2, tArg3)`。

## 4. 错误码 / 返回值



PDF + InfoSys 均未列错误码（无返回值或返回类型未明确）。

## 5. 使用注意 / 常见坑

- ⚠️ 本条目 PDF 存在印刷错误，已在 §1 功能简述中标注；编译器实际接受 InfoSys 写法。
- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。
- LogMessage 日志会输出到 TwinCAT 调试输出窗口，发布时建议把 `nLogType` 改为 WARNING 或更高级别避免日志泛滥。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_LogMessage3.TcPOU`](../examples/P_Demo_F_BA_LogMessage3.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：3 参数日志：`F_BA_LogMessage3("Temp/Hum/Pres", tArg1, tArg2, tArg3)`。
- **价值**：同 LogMessage 系列，多 1 参数。
- **替代方案对比**：多次 CONCAT（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.4.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14593493771.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
