# F_ToASC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Character functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31048715.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ToASC.xml`](../examples/P_Demo_F_ToASC.xml) |

---

## 1. 功能简述

F_ToASC 是同步函数：把 STRING **第一个字符**转换为对应的 ASCII 字节码返回。空串返回 0。常用于读取通讯报文首字节做协议判别、把 HMI 输入的单字符转字节存储等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    str : STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `str` | `STRING` | - | 要转换的字符串。仅首字符被转换；空串返回 0。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 BYTE（首字符的 ASCII 码）*)
FUNCTION F_ToASC : BYTE
```

FUNCTION 返回值类型：`BYTE`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步即出值。只取字符串首字符的 ASCII 字节，其余字符被忽略。

**空串语义**：PDF 明确——传入空字符串 `''` 时返回 `0`。这与 `'\0'`（首字符为 null）不易区分；想区分先用 `LEN()` 判长度。

**典型用法**：(1) 把 HMI 文本框首字符当作命令字（如 'R' 命令复位、'S' 命令启动）；(2) 通讯帧首字节做协议判别；(3) 单字符转字节存到配置区。

**对照**：与 `F_ToCHR` 互为反函数——前者 STRING→BYTE（首字符），后者 BYTE→STRING(1)。

**陷阱**：只看首字符；想转整个字符串到字节数组应循环用本函数 + `MID()`，或直接 `MEMCPY`。

## 4. 错误码 / 返回值

本函数不暴露错误输出。空串返回 0；非 ASCII（扩展字符）值取决于 PLC 字符集编码（⚠️ PDF/InfoSys 未明确，工程上认为按字面字节返回）。

## 5. 使用注意 / 常见坑

- **只取首字符**——不是返回字符串总字节长度，也不是返回整串编码（PDF 明确）。
- 空串返回 0，与首字符为 null 同值；要区分先 `LEN()`。（工程经验补充）
- 反方向用 `F_ToCHR`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ToASC.xml`](../examples/P_Demo_F_ToASC.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 文本框收到操作员输入命令字（'R' = reset, 'S' = start, 'P' = pause），PLC 用本函数取首字符 ASCII 做 `CASE` 跳转，简化命令派发。
- **价值**：替代 `IF str = 'R' THEN ... ELSIF str = 'S' THEN ...`（每次都做字符串比较），改为 CASE BYTE 比较更快。
- **替代方案对比**：单字符首字节用本函数；要分析整串内容用 `MID` + 循环。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31048715.html
- **相关 FB / FC**：`F_ToCHR`（反方向）
