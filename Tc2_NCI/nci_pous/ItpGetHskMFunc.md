# ItpGetHskMFunc

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NCI` |
| Library Version | `2.15.1` |
| Type | `FUNCTION` |
| Category | `NCI POUs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3284728331.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ItpGetHskMFunc.TcPOU`](../examples/P_Demo_ItpGetHskMFunc.TcPOU) |

---

## 1. 功能简述

`ItpGetHskMFunc` 读出当前通道里待处理的 Handshake M 函数号；若没有待处理则返回 0。配合 `ItpConfirmHsk` 完成『M 函数触发 → PLC 处理 → 回执 → NCI 继续』的握手循环。

## 2. 接口定义

### VAR_INPUT

无（本 POU 无 `VAR_INPUT` 参数）。

### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sNciToPlc : NCTOPLC_NCICHANNEL_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNciToPlc` | `NCTOPLC_NCICHANNEL_REF` | NCI → PLC 方向的循环通道接口结构（只读），类型 `NCTOPLC_NCICHANNEL_REF`，需在 System Manager Link 给输入映像 `AT %I*` |

### 返回值（FUNCTION）

| 名称 | 类型 | 说明 |
|---|---|---|
| `ItpGetHskMFunc` | `INT` | 当前通道里等待 PLC 处理的握手 M 函数号；为 0 时表示没有待处理的握手 M 函数 |

## 3. 行为说明

`ItpGetHskMFunc` 是纯函数（FC），调用即返回结果，不走 ADS 调用、不依赖 `bExecute` 上升沿、也没有 `bBusy` / `bErr` 状态机。实现上只是从 `sNciToPlc` 循环通道接口镜像（由 NC 端每个 PLC 周期写到 NCTOPLC 输入区）里读出对应字段，把已经在内存里的数据组装成返回值返回出去。整个过程不会修改任何 NC 状态、不会产生副作用，因此可以在 PLC 程序的任意位置任意上下文里反复调用，多调用一次只是多做一次内存读取（百纳秒级开销）。

因为没有命令状态机，本 FC 不存在『超时』『错误号』『复位』之类的问题；唯一可能的『失败』是 `sNciToPlc` 没在 System Manager 里 Link 给真实 NCI 通道接口——此时镜像内存全为 0，本 FC 会读出全 0/默认值，**没有显式错误指示**。这种『静默失败』在 PLC 端难以从返回值直接定位，建议在调用前先用 `ItpHasError(sNciToPlc)` + `ItpGetError(sNciToPlc)` 做一次通道级错误轮询，确认 cyclic interface 在正常工作再消费本 FC 的返回值。

## 4. 错误码 / 返回值

`ItpGetHskMFunc` 是纯函数（FC），不通过 `bErr` / `nErrId` 输出错误：调用即返回，返回值直接给到 `ItpGetHskMFunc` 调用表达式。如果 cyclic channel interface 配置不对（如 `sNciToPlc` 没 Link 给 NC），返回值会读到 0 或异常值——这种『静默失败』在 PLC 端难直接定位，建议把 `ItpHasError(sNciToPlc)` 与 `ItpGetError(sNciToPlc)` 配合做通道级错误轮询。

## 5. 使用注意 / 常见坑

- **`sNciToPlc` 必须先 Link 给 NCI 通道**：在 System Manager 里把 PLC 端 `AT %I*` 的 `NCTOPLC_NCICHANNEL_REF` 实例 Link 给对应通道的 NCTOPLC 接口；不 Link 等于 NCI 通道镜像全 0，所有读取类 FB 拿到的都是 0。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ItpGetHskMFunc.TcPOU`](../examples/P_Demo_ItpGetHskMFunc.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// FUNCTION 调用——返回值直接赋给本地变量观察
ItpGetHskMFunc_ret := ItpGetHskMFunc(sNciToPlc := sNciToPlc_inst);

```

## 7. 业务场景与实际价值

- **场景**：NCI 通道日常操作（启停 / Override / 加载程序 / 读写 R 参数 / 工具表 / 零点表 / M 函数握手 / 错误读取）。
- **价值**：把『裸 ADS 调用』包装成『有命名的 PLC FB』，让控制逻辑代码更易读、错误处理更显式。
- **替代方案对比**：① 直接走 ADS Read/Write → 要熟悉 NC ADS index 表；② 走 Tc2_System.ADSRDWRTEX → 接口通用但不易读；③ 本 FB 是 Beckhoff 推荐的标准做法。

## 8. 参考资料

- **PDF**：[TF5100_TC3_NC_I_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf) §7.1.2.17
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf5100_tc3_nc_i/3284728331.html
- **相关 FB / FC**：见 §3 行为说明

