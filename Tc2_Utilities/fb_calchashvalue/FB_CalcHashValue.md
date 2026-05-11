# FB_CalcHashValue
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/ |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Verified | 2026-05-11 ✅ |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CalcHashValue.xml`](../examples/P_Demo_FB_CalcHashValue.xml) |

---
## 1. 功能简述

This function block calculates a hash value. For this purpose the methods start(), update() and finish() are used. The methods decouple the appending of input data from the actual calculation of the hash value and also allow input data to be appended piece by piece in multiple steps. If it is not necessary to add input data multiple times, it is recommended to use the function F_GenerateHashValue() [ }   314 ]  instead of the function block.

## 2. 接口定义

### VAR_INPUT

无 VAR_INPUT（FB 自身无引脚；所有输入通过方法参数传入）。

### VAR_OUTPUT

无 VAR_OUTPUT（FB 自身无引脚；所有输出通过方法的 REFERENCE/PVOID 参数返回）。

### VAR_IN_OUT

无。

### 方法（Methods）

| 方法 | 描述 |
|---|---|
| [`start`](start.md) | 用指定的 hash mode 初始化 hash 计算 |
| [`update`](update.md) | 可多次调用，每次追加一段输入数据 |
| [`finish`](finish.md) | 执行 hash 计算并输出 hash 值到缓冲区 |

## 3. 行为说明

- 三个方法 `start()` / `update()` / `finish()` 把"追加数据"与"实际 hash 计算"解耦，允许分多步追加数据；
- 若不需要分步追加，推荐直接使用函数 `F_GenerateHashValue()`；
- 详细行为以 PDF 第 3.10 节为准（⚠️ 各 method 返回类型/错误码请对照在线 InfoSys 进一步细化）。

## 4. 错误码 / 返回值

`start()` 与 `update()` 在 PDF 中声明为 `METHOD <name> : BOOL`（返回值类型为 `BOOL`）。`finish()` 在 PDF 渲染中**省略了 METHOD 头**（仅给出 VAR_INPUT 与 Name/Description 表），返回值类型 ⚠️ 待人工对照在线 InfoSys 确认。

## 5. 使用注意 / 常见坑

- 调用顺序必须是 `start → (update)* → finish`；
- `update` 可以重复调用，每次追加一段数据；
- `finish` 接受一个由调用方提供的缓冲区（`pHash`），缓冲区大小 `nHash` 必须**匹配所选 hash 模式的输出长度**（详见 `E_HashMode`）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue.xml`](../examples/P_Demo_FB_CalcHashValue.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_CalcHashValue
VAR
    fbCalc      : FB_CalcHashValue;
    eMode       : E_HashMode := E_HashMode.HashMode_Sha512;
    sInput      : STRING(255) := 'hello world';
    aHash       : ARRAY[0..63] OF BYTE;     // SHA-512 = 64 bytes
    bStart      : BOOL;
    bUpdate     : BOOL;
    bFinish     : BOOL;
END_VAR

// 三阶段串联调用：start → update → finish
bStart  := fbCalc.start(hashMode := eMode);
bUpdate := fbCalc.update(pData := ADR(sInput), nData := LEN(sInput));
bFinish := fbCalc.finish(pHash := ADR(aHash), nHash := SIZEOF(aHash));
// 在线监视 aHash 字节数组观察结果
```

## 7. 相关

- 见 [`Tc2_Utilities README`](../README.md) 同库其他条目
- 各方法详见上方方法表
- 同库可替代函数：`F_GenerateHashValue()`（一次性 hash）

## 8. 待确认项

- `finish()` 返回类型未在 PDF 显式给出（⚠️ 待人工对照在线 InfoSys 确认；按 start/update 模式推断为 BOOL，但未写入文档）。
