# FB_CalcHashValue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674253067.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CalcHashValue.xml`](../examples/P_Demo_FB_CalcHashValue.xml) |

---

## 1. 功能简述

`FB_CalcHashValue` 是 Tc2_Utilities 提供的"分段式 hash 计算"功能块（Function Block, FB）。它把"喂数据"与"得结果"解耦成三个独立方法，调用顺序固定为 `start()` → `update()`（一次或多次）→ `finish()`：

- `start(hashMode)` 初始化内部上下文并选择算法（如 SHA-512）
- `update(pData, nData)` 把一段数据"喂"进去，可以反复调用直到所有输入数据喂完
- `finish(pHash, nHash)` 完成最终运算并把 hash 输出到调用方提供的缓冲区

这种"分段喂入"对大文件 / 流式数据 / 跨多周期增量数据特别合适——无需把整个输入先攒在内存里再调一次性接口。

对短输入数据（一次性已知全部数据），PDF 与 InfoSys 都推荐改用更简单的 `F_GenerateHashValue()` 函数，一行调用直接出结果，无需 `start/update/finish` 三步。

## 2. 接口定义

### VAR_INPUT

FB 本体无 `VAR_INPUT` 引脚。所有输入通过方法参数传入。

### VAR_OUTPUT

FB 本体无 `VAR_OUTPUT` 引脚。Hash 结果通过 `finish()` 的输出缓冲区（`pHash` 指向的内存）返回。

### VAR_IN_OUT

无。

### 方法（Methods）

| 方法 | 返回 | 描述 |
|---|---|---|
| [`start`](start.md) | `BOOL` | 初始化 hash 上下文，选定 `E_HashMode`。重新计算前必须先调一次 |
| [`update`](update.md) | `BOOL` | 喂一段数据到 hash 上下文。可调用 0、1 或多次（0 次时 `finish` 计算空输入的 hash） |
| [`finish`](finish.md) | （PDF 省略返回类型 ⚠️） | 计算最终 hash 并写入调用方缓冲区。缓冲区必须足够大 |

## 3. 行为说明

调用顺序约定：`start(hashMode) → update(pData, nData) → ... → update(pData, nData) → finish(pHash, nHash)`。

`start` 是必经的初始化点：它选定算法、清空内部累加状态。忘了调 `start` 直接 `update` 或直接 `finish`，行为未定义（PDF 未明说，但 hash 上下文未初始化等于输出不可预期）。

`update` 可以零次或多次调用。零次：相当于对空输入做 hash（数学上有意义——空字符串的 SHA-512 是一个确定常量）。一次：与 `F_GenerateHashValue` 等价。多次：增量式累积，常用于"大文件分块读取并 hash"或"跨多个 PLC 周期累积数据"。

`finish` 是消费点：调用后内部上下文被视为"已消耗"，再次 `update` 或再次 `finish` 的行为 PDF 未定义 ⚠️。需要重新计算 hash 必须重新调 `start`。

hash 长度由 `hashMode` 决定：在 `finish` 前调用方必须根据所选模式分配足够大的缓冲区——SHA-256 需 32 字节、SHA-512 需 64 字节。`nHash` 输入必须大于等于所选模式实际输出字节数。

FB 实例是有状态的：同一实例不能并行用于两个 hash 计算（一个 `start/update/finish` 还没完，另一个 `start` 会清掉前者的状态）。多源并行 hash 需要多个 FB 实例。

线程模型：方法调用是同步的，单 PLC 周期内调用栈完成，不存在 busy / 异步等待。但大块数据的 `update` 会消耗当周期的执行时间——把 1 MB 一次性 `update` 进去可能让本周期超时。建议每周期 `update` 几 KB 到几十 KB。

## 4. 错误码 / 返回值

- `start`：`BOOL`，`TRUE` 表示初始化成功。`FALSE` 时具体错误条件 PDF 未列 ⚠️。
- `update`：`BOOL`，`TRUE` 表示这次喂入成功。`FALSE` 时具体错误条件 PDF 未列 ⚠️。
- `finish`：PDF 在 finish 节内省略了 `METHOD finish : <RET>` 头，仅给出 `VAR_INPUT` 与参数表。InfoSys 同样省略返回类型 ⚠️。按 start / update 的模式推断为 `BOOL`，但未在 PDF 显式声明。保守用法：不强依赖返回值，调用后立刻在线监视 `pHash` 指向的缓冲区内容确认。

FB 本体没有 `bError` / `nErrorId` 输出——错误只能通过方法返回值或缓冲区是否被正确写入来判断。

## 5. 使用注意 / 常见坑

- 必须严格按 `start → update* → finish` 顺序调：跳步或乱序导致输出不可预期。
- 缓冲区不够大等于内存越界：`pHash` 是 `PVOID`（无类型指针），运行时不做长度检查；`nHash` 必须大于等于算法实际输出字节数。SHA-512 = 64 字节，SHA-256 = 32 字节（实际取值以 `E_HashMode` 文档为准）。缓冲区小了会越界写入相邻变量，是经典的 PLC 内存事故。
- 一次性能完成的小数据用 `F_GenerateHashValue`（PDF 与 InfoSys 都推荐）：FB 的价值在于"分段喂入"，对一次性输入不必动用 FB。
- finish 后必须重新 `start` 才能再算：复用实例做下一次 hash 必须先 `start`，否则内部状态污染。
- `pData` 必须指向有效内存且生命周期覆盖 `update` 调用：典型反例是把局部 STRING 临时变量的 `ADR(...)` 传进去，但传进去后该 STRING 被覆盖——hash 喂的就是脏数据。避免方法：用稳定的全局 / FB 内变量做数据源。
- `nData` 用字节数：`LEN(s)` 返回的是字符数（对 ASCII STRING 等同字节数，对宽字符串 / WSTRING 不同）。务必用 `SIZEOF` 或显式字节计数。
- 多线程 / 多任务并行调同一 FB 实例不安全（工程经验补充）：FB 是有状态的，并发会把状态搅乱。要并行 hash 用多个实例。
- 每周期 `update` 数据量过大会影响 PLC 周期（工程经验补充）：建议每周期不超过 64 KB，大文件分多个周期处理。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue.xml`](../examples/P_Demo_FB_CalcHashValue.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：生产线 PLC 周期读取一段配方数据，把它的 SHA-256 摘要发到 MES 用于
//       数据完整性校验。配方一次读完即可，不需要分段——但用 FB 演示完整
//       start/update/finish 三段调用。
//
// 价值：MES 端只信 hash 一致；不用 hash 时 MES 拿到的"配方"可能在通讯链路
//       任何环节被静默篡改而无人察觉。一行调用得到 32 字节摘要可让数据完整
//       性问题在通讯下游立刻被发现。
//
// 验证：登录后置 bStartCalc := TRUE 触发一次完整 start→update→finish 流程；
//       在线 monitor aRecipeHash 字节数组应非全 0（成功）；与同输入数据离线
//       sha256 命令行对比可验证一致。
PROGRAM P_Demo_FB_CalcHashValue
VAR
    fbHashCalculator     : FB_CalcHashValue;
    eHashMode            : E_HashMode := E_HashMode.HashMode_Sha256;
    sRecipePayload       : STRING(255) := 'recipe-v1:tank=70C,time=120s';
    aRecipeHash          : ARRAY[0..31] OF BYTE;        // SHA-256 = 32 字节
    bStartCalc           : BOOL := FALSE;
    bStartOk             : BOOL;
    bUpdateOk            : BOOL;
    bFinishOk            : BOOL;
    bHashReady           : BOOL;
END_VAR

// 一次性算完整 hash：上升沿触发一次三段调用
IF bStartCalc THEN
    bStartCalc  := FALSE;
    bStartOk    := fbHashCalculator.start(hashMode := eHashMode);
    bUpdateOk   := fbHashCalculator.update(pData := ADR(sRecipePayload),
                                            nData := LEN(sRecipePayload));
    bFinishOk   := fbHashCalculator.finish(pHash := ADR(aRecipeHash),
                                            nHash := SIZEOF(aRecipeHash));
    bHashReady  := bStartOk AND bUpdateOk;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：
  - 配方 / 程序参数下发后做完整性校验：PLC 端算 hash 上报 MES，MES 端比对自己的版本
  - 大块固件 / 工艺文件分段写入存储后整体 hash 校验
  - 安全日志：每条事件都附 hash，链式连接形成不可篡改的审计链
- **价值**：相对于"用 CRC16 简单校验"或"靠通讯协议自带的 CRC"，SHA 系列 hash 提供密码学强度的完整性保证——攻击者无法在保持 hash 不变的前提下修改任何一字节。
- **替代方案对比**：
  - `F_GenerateHashValue`：一次性 hash 短数据，一行调用搞定，**推荐用于已知全部数据的场景**
  - 自己写 CRC：碰撞概率高，不抗篡改
  - **本 FB**：当数据来自多个周期 / 多个数据源时无可替代——这是它的核心场景

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674253067.html
- **相关函数**：`F_GenerateHashValue`（一次性 hash 短数据）
- **相关枚举**：`E_HashMode`（支持的 hash 算法清单）
- **方法**：[`start`](start.md) · [`update`](update.md) · [`finish`](finish.md)
