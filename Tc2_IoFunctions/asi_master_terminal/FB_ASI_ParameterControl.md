# FB_ASI_ParameterControl

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59157259.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ASI_ParameterControl.TcPOU`](../examples/P_Demo_FB_ASI_ParameterControl.TcPOU) |

---

## 1. 功能简述

所有 ASI FB 的后台通讯调度器。必须循环调用（每个 PLC 周期一次）。它从共享的 `stParameterBuffer` 取出待执行命令、调度到 ASI 主端子的过程数据（`stParameter_IN` / `stParameter_OUT`）发送、把响应填回缓冲。没有本 FB 在 task 里跑，其它 ASI FB 全部不工作。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stParameterBuffer : ST_ParameterBuffer;
    stParameter_IN : ST_Parameter_IN;
    stParameter_OUT : ST_Parameter_OUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stParameterBuffer` | `ST_ParameterBuffer` | 参数 `stParameterBuffer`（类型 `ST_ParameterBuffer`）。 |
| `stParameter_IN` | `ST_Parameter_IN` | ASI 主端子（KL6201 / EL6201）输入过程数据；用 `AT %I*` 链到 System Manager。 |
| `stParameter_OUT` | `ST_Parameter_OUT` | ASI 主端子（KL6201 / EL6201）输出过程数据；用 `AT %Q*` 链到 System Manager。 |

## 3. 行为说明

每次任务周期被调用：① 看 `stParameterBuffer` 里是否有挂起的 ASI 命令（来自其它 ASI FB）；② 有则把命令写到 `stParameter_OUT`（ASI 主端子下行过程数据）；③ 读 `stParameter_IN`（ASI 主端子上行过程数据）拿到响应；④ 把响应回填到 `stParameterBuffer`，让发起命令的 ASI FB 在下一个周期读到 `bBusy = FALSE`。**调用契约**：放在 PlcTask 循环最末或最前，**每周期调一次**，所有 ASI FB 实例必须传同一个 `stParameterBuffer`。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **必须循环调用 `FB_ASI_ParameterControl`**，它是所有 ASI FB 的后台通讯调度器。不调它，其它所有 ASI FB 都不会动。
- `stParameterBuffer : ST_ParameterBuffer` 是全局共享缓冲：所有 ASI FB 实例 + `FB_ASI_ParameterControl` 必须传同一个实例，否则后台调度无法工作。（工程经验补充）
- `stParameter_IN` / `stParameter_OUT` 必须 **链到 System Manager 中 ASI 主端子（如 KL6201 / EL6201）的过程数据**——通过 AT %I* / AT %Q* 映射；不链则 ASI 通讯通道根本没建立。（工程经验补充）
- `bBusy = TRUE` 只表示 *命令被接受*，**不是命令被执行**。具体执行是否完成需要看 `bErr` + `iErrornumber` 在 `bBusy` 落回后的状态。（工程经验补充）
- ASI 命令专用错误码（`bErrornumber` / `iErrornumber`）见 ASI 主端子文档（KL6201/EL6201 手册）——PDF 未列入本节，调用方需要查 ASI master 错误码表。（工程经验补充）
- **这是 ASI 库的中枢，必须每个 PLC 周期循环调用**，否则所有 ASI 操作都卡住在 `bBusy = TRUE`。
- 多个 ASI 主端子时（极少见但有）需要为每个端子分别实例化本 FB + 独立的 `stParameterBuffer`，不能共用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ASI_ParameterControl.TcPOU`](../examples/P_Demo_FB_ASI_ParameterControl.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：任何使用 ASI 的工程：本 FB 是整个 ASI 库的中枢，必须循环调用一次。
- **价值**：把 ASI 通讯调度集中到一个 FB 实例，业务侧只需调用 `FB_ASI_*` 系列即可异步发命令。
- **替代方案对比**：
  - 不调用：所有 ASI FB 都卡住
  - **本 FB**：必须有

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59157259.html
- **相关 FB / FC**：`FB_ASI_Addressing`, `FB_ASI_SlaveDiag`, `FB_ASI_ReadParameter`
