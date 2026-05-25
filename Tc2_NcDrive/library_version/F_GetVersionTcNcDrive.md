# F_GetVersionTcNcDrive

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NcDrive` |
| Library Version | `1.2.9` |
| Type | `FUNCTION` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305469195.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcNcDrive.xml`](../examples/P_Demo_F_GetVersionTcNcDrive.xml) |

---

## 1. 功能简述

读取 Tc2_NcDrive PLC 库版本信息的函数（FUNCTION）。每次调用通过 `nVersionElement` 指定要读的一个版本分量，函数以 `UINT` 返回该分量的数值。常用于在代码中检查库版本，做兼容性判断或在日志中打印库版本。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_GetVersionTcNcDrive: UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nVersionElement` | `INT` | 要读的版本分量：`1` = major（主版本号）、`2` = minor（次版本号）、`3` = revision（修订号） |

### VAR_OUTPUT

无（结果通过函数返回值 `UINT` 给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回语义**：函数根据 `nVersionElement` 取库版本号的一个分量并作为 `UINT` 返回。`nVersionElement = 1` 返回 major、`= 2` 返回 minor、`= 3` 返回 revision。要拿到完整版本（major.minor.revision）需分别调用三次。

**典型用法**：在初始化阶段读三次拼出版本字符串，或单独读 major 做"库版本至少为 X"的判断。函数是无副作用的纯计算，可在任意周期任意位置直接调用，不需要边沿或 Busy 处理。

**取值范围**：PDF 仅列出 1 / 2 / 3 三个有效参数。⚠️ 传入 1-3 之外的值时返回行为 PDF 与 InfoSys 均未说明，建议不要传其他值。

## 4. 错误码 / 返回值

本函数返回 `UINT`：

| 返回 | 类型 | 含义 |
|---|---|---|
| `F_GetVersionTcNcDrive` | `UINT` | `nVersionElement` 指定分量的数值（major / minor / revision 之一） |

⚠️ 无独立错误输出；PDF / InfoSys 未定义非法 `nVersionElement` 的错误返回。

## 5. 使用注意 / 常见坑

- **一次只读一个分量**：要完整版本得调 3 次（major/minor/revision），别期望一次拿全。
- **没有 build 字段**：本函数只覆盖 major/minor/revision 三项。
- **非法参数行为未定义**：只传 1 / 2 / 3，工程经验补充别传其他值。
- **纯函数无状态**：不用边沿、不用 Busy，直接赋值调用即可。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcNcDrive.xml`](../examples/P_Demo_F_GetVersionTcNcDrive.xml)

```iecst
// 场景：上电初始化时把 Tc2_NcDrive 库版本读出来，拼成 "x.y.z" 写进诊断日志/HMI
PROGRAM P_Demo_F_GetVersionTcNcDrive
VAR
    iMajor    : UINT;
    iMinor    : UINT;
    iRevision : UINT;
    bReadOnce : BOOL := TRUE;     // 只在首周期读一次
END_VAR

// 纯函数，无需边沿/Busy；首周期读三个分量即可
IF bReadOnce THEN
    iMajor    := F_GetVersionTcNcDrive(nVersionElement := 1);
    iMinor    := F_GetVersionTcNcDrive(nVersionElement := 2);
    iRevision := F_GetVersionTcNcDrive(nVersionElement := 3);
    bReadOnce := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：诊断信息收集、库版本兼容性自检、在 HMI / 日志中展示当前 Tc2_NcDrive 库版本。
- **价值**：在运行期就能拿到实际链接进工程的库版本，避免靠人工记忆或翻 manifest；做"低于某版本则告警"的兼容性门槛检查很方便。
- **替代方案对比**：
  - 若库提供 `stLibVersion_Tc2_NcDrive` 全局版本结构常量：一次读全部字段更省事
  - **本函数**：每次取一个分量的轻量方式，老代码常见

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf) §3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305469195.html
- **相关条目**：库版本检查相关全局常量 / `F_CmpLibVersion`（版本比较）
