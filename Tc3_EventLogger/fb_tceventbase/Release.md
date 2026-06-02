# Release

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5053026955.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_Release.TcPOU`](../examples/P_Demo_Release.TcPOU) |

---

## 1. 功能简述

`FB_TcEventBase.Release()` 显式释放 EventLogger 内部为当前事件实例分配的槽位。

**仅用于动态分配**（`__NEW` / `__DELETE`）的事件实例。静态声明的 `VAR fbAlarm : FB_TcAlarm;` 不需要调 Release——实例销毁时 FB_exit 会自动处理。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用一次释放一次。调用后这个 FB 实例上的方法都会失败——Raise / Clear / Confirm 都拿不到 EventLogger 槽位，事件无法分发也无法持久化。因此 Release 之后必须立即丢弃该实例（清指针 + __DELETE）。

**典型用法**：工程支持运行时动态新增/删除报警点（例如根据当前加载的配方动态生成不同报警），每个动态报警用 `__NEW(FB_TcAlarm)` 分配，配方切换时把不再需要的报警先 Release 再 __DELETE。静态声明（`VAR fbAlarm : FB_TcAlarm;`）的实例由 FB_exit 自动处理回收，**不需要也不应该**手动 Release。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 成功释放 | 之后不要再调任何方法 |
| `其他错误` | 已释放 / 无效实例 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 静态实例（VAR 声明）**不要**调 Release——会让 EventLogger 槽位提前回收，下次扫描 Raise 失败。
- `__DELETE` 之前必须先 Release，否则 EventLogger 内部留下悬挂引用。
- Release 后实例视为已废弃，不要再调任何方法。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_Release.TcPOU`](../examples/P_Demo_Release.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

工程支持运行时新增/删除报警点（动态配方），每次删除前必须释放 EventLogger 槽位


保证 EventLogger 资源不泄露，长时间运行的 PLC 也不会因为反复 Create/Delete 耗尽槽位


不释放直接 `__DELETE` → 槽位泄露，长时间运行后 EventLogger 拒绝新事件；全部用静态实例 → 简单但无法动态调整报警点


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5053026955.html
- **相关**：`FB_TcAlarm`, `FB_TcMessage`
