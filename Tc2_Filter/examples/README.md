# Tc2_Filter / examples

每个 FB 配套的可导入演示程序，**TwinCAT 3 原生 .TcPOU 格式**（XML / TcPlcObject schema），可直接拖入 XAE 的 PLC `POUs` 文件夹。

## 命名约定

- `P_Demo_<Name>.TcPOU` — 一个 PROGRAM POU，演示该滤波器 FB 的最小可运行用法

## 统一的演示套路（滤波类）

本库所有例程结构一致，因为 15 个 FB 接口一致：

1. 声明时用 `stConfig` 直接配置滤波器（`fbFilter : <FB>(stConfig := stParams);`，故上电即 `bConfigured = TRUE`）。
2. 每个周期合成一个测试信号 `fNoisyIn`：**1 Hz 正弦基波**（幅值 10）+ 可在线注入的**周期性尖峰扰动**。
3. 用 `fbFilter.Call(ADR(aIn), SIZEOF(aIn), ADR(aOut), SIZEOF(aOut))` 把信号送入滤波器，取出 `fFilteredOut`。
4. 在线同时 monitor `fNoisyIn` 与 `fFilteredOut`，对照观察滤波效果。

> 输入/输出用单通道、单过采样的 `ARRAY [1..1] OF ARRAY [1..1] OF LREAL`（即 `nOversamples = 1`、`nChannels = 1`）。

## 如何导入到 TwinCAT 3 XAE

1. 在 Solution Explorer 里**右键 PLC 项目（`<MyProject> Project` 节点）或其下任一文件夹**
2. 选 **"Add → Existing Item..."**
3. 选中本目录下的 `.TcPOU` 文件
4. 弹窗显示可导入对象（一个 PROGRAM）→ OK
5. POU 出现在树中（顶层或你选的文件夹下，取决于 TwinCAT 设置）

> ⚠️ 一定要**右键 PLC 项目层**（不是 Solution 层、不是 System 层），否则菜单不会出现 "Add → Existing Item"。

## 如何运行验证

1. 引用 `Tc2_Filter` 库（References → Add library）
2. 编译 PLC 项目（无错误）
3. 把导入的 PROGRAM 加到任务调用列表。**因为例程的 `fSamplingRate = 1000`，请用一个周期为 1 ms 的任务调用本 POU**，让采样率与调用频率一致——这样滤波器的时间常数 / 截止频率才与设计值相符。
   - 在某个 1 ms 任务里加一行 `P_Demo_FB_FTR_PT1();`（或对应名）
4. Activate Configuration → 登录 → Run
5. 在线 monitor：
   - `bConfigured` 应为 `TRUE`
   - `fFilteredOut` 应是 `fNoisyIn` 的滤波版本（平滑 / 相位校正 / 延迟，视滤波器类型而定）
   - 在线把 `bInjectSpike` 写 `TRUE` 注入尖峰，观察 `fFilteredOut` **不会立刻跟随尖峰**，而是被滤波器抑制——以此确认『滤波器真的在做事』

每个 .TcPOU 文件顶部注释列出了该 demo 的场景、价值与具体验证步骤。

## 库依赖

- `Tc2_Filter`（TF3680，需对应授权）
- 读取 `ipResultMessage` 详情时可配合 `Tc3_EventLogger`（可选）
