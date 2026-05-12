# ExtendName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcSourceInfo` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050998795.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ExtendName.xml`](../examples/P_Demo_ExtendName.xml) |

---

## 1. 功能简述

`FB_TcSourceInfo.ExtendName()` 给现有 SourceName 追加一个后缀字符串。

典型用法：默认 SourceName 是 PLC 符号路径（如 `MAIN.fbMotor`）；在多工位场景下用本方法加上工位号（变成 `MAIN.fbMotor.Station-01`），让事件能精确定位。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sExtension : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sExtension` | `STRING(255)` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用即同步执行：内部 SourceName 字符串后面追加 `sExtName` 内容形成新的 SourceName。多次调用会**累加**而不是覆盖——再调一次会在已经扩展过的 SourceName 后面再加一个后缀，因此通常只调用一次。

**典型用法**：FB_init 里调一次 ExtendName 给本工位的 SourceInfo 加唯一标识符（如 `Station-01`），之后所有 alarm 共享这个 SourceInfo 实例都自带工位号。多工位共用同一份 PLC 代码时，每个工位实例独立 ExtendName 加自己的工位号，让 EventLogger 在事件日志里能精确区分哪台设备出的事件。STRING 字段总长度不要超过 256 字节。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 后缀已追加 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 多次调用累加——避免在循环里反复调，否则 SourceName 越来越长。
- 追加 SourceName 后已存在的 alarm 不受影响——只对新建/新事件生效。
- STRING 长度有限——`SourceName` 字段总长建议不超过 256 字节。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ExtendName.xml`](../examples/P_Demo_ExtendName.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

多工位代码复用：每个工位的 SourceInfo 实例 ExtendName 一次本工位号


事件追溯天然带工位标识，无需自建映射表


直接 setter 重写 SourceName → 适合完全覆盖；本方法适合"在默认基础上加后缀"


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.12.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050998795.html
- **相关**：`FB_TcSourceInfo`, `FB_TcSourceInfo.Clear`, `FB_TcSourceInfo.ResetToDefault`
