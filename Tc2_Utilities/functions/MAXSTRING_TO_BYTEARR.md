# MAXSTRING_TO_BYTEARR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35145227.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_MAXSTRING_TO_BYTEARR.xml`](../examples/P_Demo_MAXSTRING_TO_BYTEARR.xml) |

---

## 1. 功能简述

把 STRING 转为字节数组——`BYTEARR_TO_MAXSTRING` 的反向；按 ASCII 逐字节复制。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : T_MaxString;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_MaxString` | — | 源 STRING。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `ARRAY[0..MAX_STRING_LENGTH] OF BYTE` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：把 `in` 中的字节（直到 null）复制到输出数组的对应位置，剩余位置写 0。**字节数组容量** = `MAX_STRING_LENGTH + 1`（默认 256）。STRING 中遇到 null 即停，后续字节为 0。**用途**：把 PLC STRING 直接送到只接受字节数组接口的设备（如老 ModBus 寄存器、二进制协议字段）。

## 4. 错误码 / 返回值

返回 `ARRAY[0..MAX_STRING_LENGTH] OF BYTE`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **输出数组大小固定** = `MAX_STRING_LENGTH + 1`（256）；不可更短。
- **STRING null 之后是 0**——不是源 STRING 缓冲的残留数据。
- **对称函数 `BYTEARR_TO_MAXSTRING`**。
- 返回是数组（值类型），赋值时整 256 字节都被复制——对性能敏感场景留意。
- **类型固定 `T_MaxString` = STRING(255)**——长字符串需先 `STRNCPY` 截到 255。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MAXSTRING_TO_BYTEARR.xml`](../examples/P_Demo_MAXSTRING_TO_BYTEARR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把配置文件中的 STRING 标签写入 ModBus 寄存器区（按字节数组对齐）。
- **价值**：替代手写 FOR + 字节复制；本函数 1 调用。
- **替代方案对比**：`BYTEARR_TO_MAXSTRING`：反向；`MEMCPY`：手动版本。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.57 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35145227.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
