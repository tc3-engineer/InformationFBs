# FB_JsonReadWriteDataType

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220231435.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonReadWriteDataType.TcPOU`](../examples/P_Demo_FB_JsonReadWriteDataType.TcPOU) |

---

## 1. 功能简述

`FB_JsonReadWriteDataType` 提供基于 PLC 符号信息（symbol info）的 JSON 自动序列化与反序列化。无需手写每个字段的 Add/Get，通过 AddJsonValueFromSymbol / SetSymbolFromJson 等方法直接在 PLC 结构体变量与 JSON 之间双向转换。支持 PLC attribute 注解控制 JSON key 名、属性元数据。需启用 SYSTEM → Settings 的 UTF-8 符号支持。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

实例化后即可通过 `AddJsonValueFromSymbol(...)` 等方法把 PLC 符号表中的变量值自动转为 JSON 写入 SAX writer；或通过 `SetSymbolFromJson(...)` 把接收到的 JSON 反向赋回符号表里的变量。依赖 ADS 符号信息，因此调用前需要确保 TwinCAT 工程已启用符号上传（System → Settings → Generate symbols for IO checks）。若结构体成员带 `{attribute 'json' := '<keyname>'}` 注解，JSON key 会用注解值而非默认成员名；搭配 PLC attribute 还可控制可选/必选、默认值等元数据。UTF-8 字符需要启用 SYSTEM → Settings 的 UTF-8 符号支持。

## 4. 错误码 / 返回值

本功能块/方法无返回值。状态通过 `initStatus` / `bError` / `hrErrorCode` 等输出反馈。

## 5. 使用注意 / 常见坑

- 实例化后先检查 VAR_OUTPUT 中的 `initStatus`，确认 FB 初始化成功（`S_OK`）再调业务方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonReadWriteDataType.TcPOU`](../examples/P_Demo_FB_JsonReadWriteDataType.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：控制系统配方数据存为结构体，需要把整个结构体一次性转 JSON 上传 / 接收 JSON 后整体回写。
- **价值**：通过符号信息全自动转换；增删字段不用改 JSON 序列化代码，加 `attribute` 即可。
- **替代方案对比**：手写每个字段的 AddKey + AddString → 结构体一改就漏字段；用 OPC UA → 协议受限。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4220231435.html
- **相关 FB / FC**：`FB_JsonSaxWriter`, `FB_JsonDomParser`
