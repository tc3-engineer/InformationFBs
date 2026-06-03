# FB_Rec_Teach_In_Ex

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Teach-in receive (extended)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/3265337739.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Rec_Teach_In_Ex.TcPOU`](../examples/P_Demo_FB_Rec_Teach_In_Ex.TcPOU) |

---

## 1. 功能简述

`FB_Rec_Teach_In` 的**扩展版本**（Ex 后缀）——在原版基础上**额外检查电报是否符合 EEP（EnOcean Equipment Profile）4-byte teach-in 格式**，对应输出结构改为 `STR_Teach`（含 `nFunc` 而不是 `nProfile`）。EEP 4-byte teach-in 是 EnOcean Alliance 推动的"自描述"标准——按学习按键时设备会把自己的 manufacturer ID、type、function 三字段一起播报，配套 EnOcean Alliance EEP 表可以**反查"设备是几键面板还是温控还是窗磁"**，做工程时无须再翻设备手册。

需要 TwinCAT 3.1.4020.32 / Tc2_EnOcean 3.4.6.0 及以上版本（PDF Prerequisites）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart     : BOOL;
    byNode     : BYTE;
    str_KL6581 : STR_KL6581;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 电平：TRUE 开启监听 |
| `byNode` | `BYTE` | — | KL6583 节点过滤；`0` 监听全部 |
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bLearnType   : BOOL;
    by_Node      : BYTE;
    dw_ID        : DWORD;
    str_Teach_In : STR_Teach;
    bReceive     : BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bLearnType` | `BOOL` | TRUE 时 `str_Teach_In` 含有有效 EEP 三字段 |
| `by_Node` | `BYTE` | 接收节点编号（同 `FB_Rec_Teach_In` 描述错误备注：PDF 写 "Number of EnOcean® devices found" 实际是节点号） |
| `dw_ID` | `DWORD` | 按下学习按键的设备 EnOcean ID |
| `str_Teach_In` | `STR_Teach` | EEP 字段：`nManufacturerID (WORD) / nTYPE (BYTE) / nFunc (BYTE)`（注意：与 `FB_Rec_Teach_In` 的 `STR_Teach_In` 第三字段不同——这里是 `nFunc`） |
| `bReceive` | `BOOL` | **反相脉冲**，新事件到达时 FALSE 一周期 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 电平。

**Ex 版的不同**：
- 额外做"是否 EEP 4-byte teach-in"检查；只在格式合法时才置 `bLearnType = TRUE`。
- 输出 `STR_Teach` 而不是 `STR_Teach_In`（`nFunc` 替代 `nProfile`，反映新版 EEP 命名）。

**EEP 反查工作流**：
1. 工程师按设备 LRN 按键。
2. PLC 抓到 `dw_ID + bLearnType = TRUE + str_Teach_In.{nManufacturerID, nTYPE, nFunc}`。
3. 对照 EnOcean Alliance EEP 表（在线 PDF 或 Beckhoff 官方说明），用 `(nFunc, nTYPE)` 反查"这个设备属于 EEP X.YZ profile，是按键 / 温控 / 门磁"。
4. PLC 根据设备类型自动绑定到对应的接收 FB（`FB_Rec_1BS` / `FB_Rec_RPS_Switch` / 等）。

**与原版区别小结**：原版只给 ID + 部分字段；Ex 版给 ID + EEP 完整字段，可做"自描述设备识别"。

**典型陷阱**：
- 旧设备不支持 EEP 4-byte teach-in → `bLearnType = FALSE`，`str_Teach_In` 字段为 0；只能拿 `dw_ID`。
- 期待"PLC 自动 EEP 字典反查"——本 FB 不带 EEP 字典，应用层要自己维护或写 CASE。
- 把 `str_Teach_In.nProfile`（原版字段）当 `str_Teach_In.nFunc`（Ex 版字段）→ 编译报错（类型不同）。

## 4. 错误码 / 返回值

本 FB 无显式错误输出，依赖上游 `fbKL6581.iErrorID`。

## 5. 使用注意 / 常见坑

- **设备需支持 EEP**：现代 EnOcean Alliance 认证设备绝大多数支持；老式 / 厂家定制可能仅原版 teach-in 格式。
- **`str_Teach.nFunc` 是新字段**：与 `STR_Teach_In.nProfile` 类型相同 (BYTE) 但语义不同；编程时不要混用。
- **EEP 反查表自己维护**：典型代码 `CASE str_Teach.nFunc OF 16#02: (* 4 键开关 *) ... ; 16#05: (* 1BS 门磁 *) ... ; END_CASE;`
- **`by_Node` 是节点号**（PDF 描述错误同原版）。
- **新工程首选 Ex 版**：除非维护老项目，否则用 Ex 版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Rec_Teach_In_Ex.TcPOU`](../examples/P_Demo_FB_Rec_Teach_In_Ex.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Rec_Teach_In_Ex
VAR
    fbKL6581       : FB_KL6581;
    fbTeachEx      : FB_Rec_Teach_In_Ex;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bDoLearn       : BOOL := TRUE;
    nId            : DWORD;
    stEEP          : STR_Teach;
    bEEPValid      : BOOL;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbTeachEx(
    bStart       := bDoLearn,
    byNode       := 0,
    str_KL6581   := fbKL6581.str_KL6581,
    bLearnType   => bEEPValid,
    dw_ID        => nId,
    str_Teach_In => stEEP
);
```

## 7. 业务场景与实际价值

- **场景**：现代楼宇项目接入大量 EnOcean Alliance 认证设备（不再是定制版）。工程师按 LRN 按键后 PLC 自动通过 EEP 三字段识别设备类型，对应绑定接收 FB——比原版 Teach_In 多一层"自描述识别"，调试效率更高。
- **价值**：EEP 反查后 PLC 自动判断"这个 ID 是 4 键面板还是门磁"，并把它路由到正确的 `FB_Rec_*` 实例；调试更省心。
- **替代方案对比**：
  - 用 `FB_Rec_Teach_In`：仅给 ID + 部分字段，类型靠工程师手动判断
  - 用 `FB_EnOcean_Search`：全网扫描，无类型信息
  - **本 FB**：新工程首选，配合 EEP 字典实现"自动设备识别 + 自动绑定"

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/3265337739.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Rec_Teach_In`（原版）、`STR_Teach`（输出结构 §4.2.2.2.6）、`FB_Rec_*`（按 EEP 识别后绑定的目标接收 FB）

## 9. 待确认项 ⚠️

- `by_Node` 字段 PDF 描述与原版 `FB_Rec_Teach_In` 一样写为 "Number of EnOcean® devices found"，本仓库按协议常识判定为节点号。
