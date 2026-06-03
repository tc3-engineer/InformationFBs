# SaveDocumentToFile

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_JsonXml` |
| Library Version | `1.14.2` |
| Type | `METHOD` |
| Category | `FB_JsonDomParser` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_JsonDomParser_SaveDocumentToFile.TcPOU`](../examples/P_Demo_FB_JsonDomParser_SaveDocumentToFile.TcPOU) |

---

## 1. 功能简述

把当前 DOM 内存中的 JSON 文档保存到磁盘文件。`bExec` 上升沿触发异步写入，完成后返回值为 `TRUE` 表示保存成功。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExec : REFERENCE TO BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExec` | `REFERENCE TO BOOL` | 执行触发位。上升沿启动异步加载；过程结束后由 FB 内部置回 FALSE。 |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hrErrorCode` | `HRESULT` | 操作失败时返回错误码（HRESULT）。`S_OK` (0) = 成功；其他值见附录 ADS Return Codes 表。 |


### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sFile : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sFile` | `STRING` | 文件路径（UTF-8 编码）。 |


## 3. 行为说明

调用机制与 `LoadDocumentFromFile` 对偶：`bExec` 上升沿启动异步写入，方法在写入完成的那一个周期返回 `TRUE`。`hrErrorCode` 给出底层文件操作的 HRESULT；常见错误为路径不存在或没有写入权限。目标文件如已存在会被覆盖。本方法属 `FB_JsonDomParser` 的对外 API，调用前需要保证父 FB 实例已成功初始化（`initStatus` 为 `S_OK`）。

## 4. 错误码 / 返回值

本方法返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 调用成功 | 继续后续逻辑 |
| `FALSE` | 调用失败 | 检查输入参数 / 调 `ExceptionRaised()` 或读 `hrErrorCode` 定位 |

## 5. 使用注意 / 常见坑

- DOM 内存只在 `NewDocument()` / `ParseDocument()` 时重新分配；频繁 Set/Add 会累积 router 内存（PDF 4.1 节明确警告）。
- 异步方法需要在 PLC 主循环里持续调用直到返回 `TRUE` 完成；不要在单个周期里 `IF .. THEN .. END_IF` 包一次就走。
- 文件必须是 UTF-8 编码；UTF-16 / Windows-1252 等会失败（PDF 24 页 Encoding 段明确说明）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_JsonDomParser_SaveDocumentToFile.TcPOU`](../examples/P_Demo_FB_JsonDomParser_SaveDocumentToFile.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：把当前生成的 JSON 文档持久化到 SD 卡，下次断电重启可继续。
- **价值**：一次调用完成异步写盘 + UTF-8 编码 + DOM 序列化。
- **替代方案对比**：拆成 GetDocument + Tc2_Utilities FB_FileOpen/Write/Close → 串行调用易漏 Close；走 ADS 同步外部存储 → 增加网络耦合。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_JsonXml_EN.pdf) §4.1.95
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_jsonxml/4219231115.html
- **相关 FB / FC**：`FB_JsonDomParser`
