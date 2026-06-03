# BAComn_Param

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `GVL` |
| Category | `GVLs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14592851723.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_BAComn_Param.TcPOU`](../examples/P_Demo_BAComn_Param.TcPOU) |

---

## 1. 功能简述

BA2_Common 字符串分词器（tokenizer）的全局参数：`nStrTokenizer_BufferSize`（缓冲条目数）与 `nStrTokenizer_MaxLevel`（嵌套深度）。本 GVL 配合内部字符串解析使用（用户一般不直接访问），标 `qualified_only`。

## 2. 接口定义

### VAR_GLOBAL

```iecst
VAR_GLOBAL CONSTANT
  {region 'Tokenizer'}
    nStrTokenizer_BufferSize  : UINT    := 32;
    nStrTokenizer_MaxLevel    : BYTE    := 5;
  {endregion}
END_VAR
```

⚠️ 这是 GVL（全局常量集合）。本表给出代表性条目；完整定义见 PDF 原文。


## 3. 行为说明

BA2_Common 字符串分词器（tokenizer）的全局参数：`nStrTokenizer_BufferSize`（缓冲条目数）与 `nStrTokenizer_MaxLevel`（嵌套深度）。本 GVL 配合内部字符串解析使用（用户一般不直接访问），标 `qualified_only`。 本 GVL 是 *只读全局常量* 集合：所有字段在 PLC 启动时已初始化为定值，运行时不允许写入（编译器静态强制）。可被任意 POU 通过 `GVL 名.字段名` 访问。 典型工程场景：调整内部 tokenizer 缓冲尺寸（极少需要修改，默认即可）。

## 4. 错误码 / 返回值

本 GVL 无返回值（全局常量集合）。

本条目无 `bError` / `nErrId` 输出（全局常量），不存在运行时错误。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BAComn_Param.TcPOU`](../examples/P_Demo_BAComn_Param.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：调整内部 tokenizer 缓冲尺寸（极少需要修改，默认即可）。
- **价值**：集中可调参数，避免散落。
- **替代方案对比**：硬编码（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14592851723.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
