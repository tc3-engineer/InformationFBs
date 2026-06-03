# FB_BA_PersistentDataHandler

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `System / Persistent Data` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/16998801291.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_PersistentDataHandler.TcPOU`](../examples/P_Demo_FB_BA_PersistentDataHandler.TcPOU) |

---

## 1. 功能简述

把 PLC 的 persistent 数据按需写盘并自动维护 `Port_xxx.bootdata` + `Port_xxx.bootdata-old` 双文件备份。区别于 TwinCAT 默认行为（仅在 Run→Config 切换时自动写盘），本 FB 让 PLC 在运行期可以在任意时刻主动把当前 persistent 值快照到磁盘，保证 retain 数据始终可恢复（断电、复位、写盘损坏都能从备份回滚）。实现 `I_BA_PersistentDataHandler` 接口。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStt                : BOOL;
    {attribute 'parameterUnit':= 's'}
    nInitSttDly         : UDINT := 10;
```

⚠️ PDF 在 VAR\_INPUT 区**缺结束标记**——是 PDF 印刷遗漏。InfoSys 一致。编译器接受（实际 VAR\_OUTPUT 段的开头会自动结束 VAR\_INPUT 段）。

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStt` | `BOOL` | - | 上升沿启动一次写盘（如果不在启动期）。启动期（`nInitSttDly` 倒计时未完）忽略此输入。 |
| `nInitSttDly` | `UDINT` | `10` | 启动延时 `[s]`：reset 或 TwinCAT 重启后此延时结束才自动写盘一次。设为 0 表示跳过自动初始化写盘。本字段带 `{attribute 'parameterUnit':= 's'}` 属性。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy               : BOOL;
    nRemTnInitSttDly    : UDINT;
    bErr                : BOOL;
    sErrDescr           : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 正在执行写盘 / 文件操作期间为 TRUE。`bBusy = TRUE` 时不接受新的 `bStt` 上升沿。 |
| `nRemTnInitSttDly` | `UDINT` | 启动延时剩余秒数。⚠️ 字段名 `nRemTnInitSttDly`——PDF 印刷错误，正确拼写为 `nRemTiInitSttDly`（InfoSys 一致）。本文档照 PDF 原样保留。 |
| `bErr` | `BOOL` | 文件读 / 写 / 打开 / 关闭出错时置 TRUE；FB 内部固定等 2 秒后会自动重试上次失败的操作。 |
| `sErrDescr` | `T_MaxString` | 错误描述字符串。出错时填，无错时为空。 |

### VAR_IN_OUT

无。

## 3. 行为说明

启动行为：reset 或 TwinCAT 重启后 FB 进入 `nInitSttDly`（默认 10）秒的"启动期"。这段时间内 `nRemTnInitSttDly` 倒数，`bStt` 输入被忽略（防止系统未稳就写盘）。倒数到 0 后 FB 自动执行一次写盘（除非 `nInitSttDly = 0` 时跳过此步）。运行期触发：`bStt` 上升沿启动一次写盘，前提是不在 `bBusy` 状态。写盘过程：① 把当前 persistent 数据写入 `Port_xxx.bootdata`（其中 xxx 是当前运行时端口号，FB 内部自动检测无需手填）；② 然后把刚写好的 `.bootdata` 复制到 `.bootdata-old` 作为备份。这样两文件始终一致，**断电时即使 `.bootdata` 损坏也能从 `.bootdata-old` 恢复**。错误处理：任何文件操作出错（FB_FileOpen / FB_FileRead / FB_FileWrite / FB_FileClose 内部用了这些来自 Tc2_Standard / Tc2_System 的 FB），FB 把错误描述填入 `sErrDescr` 并置 `bErr := TRUE`。等 2 秒后 FB 自动重试。备份恢复：TwinCAT 重启时如检测到 `.bootdata` 损坏，会自动从 `.bootdata-old` 加载——但**前提是运行时设置里 "Clear Invalid Persistent Data" 必须取消勾选**。**单实例约束**：每个 PLC 项目只允许一个 `FB_BA_PersistentDataHandler` 实例访问 persistent 文件，否则多实例会引起文件句柄冲突（PDF NOTICE 明确）。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` + `sErrDescr` 输出错误。PDF 列出的具体错误号见错误描述列：

| 错误码 | 含义 |
|---|---|
| `02 - Warning - 写 persistent 数据失败（内部 FB\_WritePersistentData 报错）` | 写 .bootdata 失败 |
| `04 - Warning - 读原始 .bootdata 文件失败（内部 FB\_FileRead 报错） + 错误号` | 读原始文件失败 |
| `06 - Warning - 关闭原始 .bootdata 文件失败（内部 FB\_FileClose 报错） + 错误号` | 关闭文件失败 |
| 其它 | PDF / InfoSys 未完整列；`sErrDescr` 给出可读描述，2 秒后内部自动重试 |

## 5. 使用注意 / 常见坑

- ⚠️ **PDF VAR\_INPUT 段缺结束标记**——是 PDF 印刷遗漏。VAR\_OUTPUT 段的开头会自动结束 VAR\_INPUT 段。
- ⚠️ **`nRemTnInitSttDly` 是 PDF 印刷错误**，InfoSys 与库内实际是 `nRemTiInitSttDly`（少了一个 `T`）。编译器只接受后者。
- **单实例约束**：每个 PLC 项目里只能用一个本 FB 实例。多实例会产生 file handle 冲突，导致 retain 写盘行为不可控。这是 PDF 显式 NOTICE 警告的。（PDF 明确）
- **运行时设置 "Clear Invalid Persistent Data" 必须 OFF**：否则 `.bootdata` 损坏后 TwinCAT 不会从 `.bootdata-old` 恢复，retain 数据全丢。在 System Manager → PLC → Runtime Settings 里检查。（PDF 明确）
- **`bStt` 是上升沿**——不要循环置 TRUE，要 `FALSE → TRUE` 边沿；常用 R_TRIG 或 HMI 按钮触发。
- **写盘期间 PLC 不会卡住**：`bBusy` 期间应用代码正常运行，FB 异步写盘；但写盘耗时 10-100 ms 数量级，频繁触发会拖累系统 I/O 负载。建议触发频率 ≥ 1 分钟一次。（工程经验补充）
- **可用 `TwinCAT_SystemInfoVarList._AppInfo.OldBootData`** 查询本次启动是否从 `.bootdata-old` 恢复——若 TRUE 说明 SD 卡/磁盘可能有问题，应报警。（PDF 提到，PlcAppSystemInfo）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_PersistentDataHandler.TcPOU`](../examples/P_Demo_FB_BA_PersistentDataHandler.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 工控机楼控应用：报警计数器、能耗累计、操作员配置都是 persistent。运行 24/7。如果纯靠 TwinCAT 默认（Run→Config 切换时才写盘），断电瞬间 retain 数据可能全部丢失（电源插头被拔时根本没机会写盘）。引入本 FB 后，每 5 分钟主动写一次盘 + 双文件备份，断电恢复后数据连续。
- **价值**：相比配 UPS 让系统正常关机（要 5-10 秒）然后写盘的"硬件方案"，本 FB 的"运行期主动写盘"是软件方案，无需 UPS 即可大幅降低断电数据损失风险。对比手写 `FB_WritePersistentData` 调用：本 FB 多了 `.bootdata-old` 备份机制，单点写盘失败时仍可恢复。
- **替代方案对比**：
  - **不主动写盘**（依赖 TwinCAT 默认 Run→Config 写）：断电时数据全丢；
  - **手调 `FB_WritePersistentData`（Tc2_Utilities）**：无双文件备份，写盘瞬间断电会损坏文件；
  - **本 FB**：双文件备份 + 启动期延时 + 自动重试 + 错误描述，是 BA 工程的标准 retain 方案。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/16998801291.html
- **相关接口**：`I_BA_PersistentDataHandler`
- **相关 FB**：`FB_WritePersistentData`（Tc2_Utilities，底层写盘）、`FB_FileOpen` / `FB_FileRead` / `FB_FileWrite` / `FB_FileClose`（Tc2_System，被本 FB 内部使用）

## 9. 待确认项 (⚠️)

- PDF VAR\_INPUT 区缺结束标记 —— 是 PDF 印刷遗漏。
- PDF VAR_OUTPUT 字段名 `nRemTnInitSttDly` 是印刷错误，InfoSys/编译器是 `nRemTiInitSttDly`。
