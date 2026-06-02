# F_ToCHR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `Character functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31047179.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ToCHR.TcPOU`](../examples/P_Demo_F_ToCHR.TcPOU) |

---

## 1. 功能简述

F_ToCHR 是同步函数：把一个 ASCII 字节（`BYTE`，如 `16#41`）转换成长度为 1 的 `STRING`（`'A'`）。常用在把字节数据可视化打印、把字节缓冲一字一字拼成 STRING 输出到 HMI 等场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    c : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `c` | `BYTE` | - | 要转换的 ASCII 字节码。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 STRING（长度 1 的字符串）*)
FUNCTION F_ToCHR : STRING
```

FUNCTION 返回值类型：`STRING`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步即出值。返回的是包含 1 个字符的 STRING（不是 1 字节）。

**典型用法**：把通讯帧里读到的字节流可视化——例如 0x31 转 `'1'`、0x41 转 `'A'`、0x0D 转 CR（回车控制符）。把多个字节循环转换后用 `CONCAT` 拼成完整字符串。

**ASCII 范围之外**：函数本身不限制输入字节值，0..255 都接受；但 ASCII 标准只定义 0..127，扩展 ASCII (128..255) 在不同 code page 含义不同——PDF 与 InfoSys 都未说明本函数对 >127 的输入如何处理（⚠️ 待人工确认），工程上认为按字面字节装入 STRING。

**对照**：与 `F_ToASC` 互为反函数——前者 BYTE→STRING(1)，后者 STRING→BYTE。

## 4. 错误码 / 返回值

本函数不暴露错误输出。对任意 0..255 字节都返回一个长度 1 字符串。

## 5. 使用注意 / 常见坑

- ASCII 控制符（0x00..0x1F、0x7F）也会被装入字符串，但 HMI / 终端不一定能正常显示。（工程经验补充）
- 字节值 >127 的处理 PDF/InfoSys 未明确，⚠️ 待人工确认；工程上认为按字面装入。
- 反方向用 `F_ToASC`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ToCHR.TcPOU`](../examples/P_Demo_F_ToCHR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：通讯报文调试——从 RS232 缓冲里读到字节流 0x48, 0x65, 0x6C, 0x6C, 0x6F，用本函数逐字节转 STRING 拼接显示 'Hello' 在 HMI 上。
- **价值**：替代手写 ASCII 转换表，一行函数完成。
- **替代方案对比**：单字节用本函数；多字节直接 `MEMCPY` 到 STRING 缓冲更快。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31047179.html
- **相关 FB / FC**：`F_ToASC`（反方向）
