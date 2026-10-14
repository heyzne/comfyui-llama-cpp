# ComfyUI-llama-cpp
在 ComfyUI 中基于 llama.cpp 框架原生运行 LLM & VLM 模型。  
**[[📃English](./README.md)]**   

## 预览
![preview](img/preview.jpg)

## 安装步骤

#### 安装节点:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/heyzne/comfyui-llama-cpp.git
python -m pip install -r ComfyUI-llama-cpp/requirements.txt
```

### 模型路径:
- 请将下载的 `.gguf` 模型放置在 `ComfyUI/models/LLM` 目录中.  

	> 在使用VLM模型进行图像推理之前, 请确保已经下载并选择了主模型对应的`mmproj`权重文件.

## 更新日志

#### v1.5.1
- **性能修复**: 优化阶段反推的帧数上限在所有模式下统一为 8 帧。此前 `one by one` / `images` 模式会逐帧全量反推 (长视频可达数百次调用, 极其耗时); 现在超过 8 帧时均匀采样 8 帧做反推与优化参考。主推理仍按所选模式处理全部帧 (`one by one` 逐张 / `video` 按 max_frames 采样)。

#### v1.5.0
- **video 输入口类型改为 IMAGE**: `Llama-cpp Instruct` 的 `video` 端口由 VIDEO 类型改为 IMAGE 类型, 可直接连接视频加载节点输出的帧序列 (如截图中的 AnimateDiff 加载器「图像」输出)。配合 `推理模式=video` 使用时, 提示词优化前会先对视频整体反推 (采样≤8 帧描述动作/运镜/时间变化)。与 images/image_N 同时连接时视频帧排在图片之后。

#### v1.4.9
- **新增 VIDEO 视频输入口**: `Llama-cpp Instruct` 节点新增 `video` 输入端口, 可直接连接 Load Video / VHS 等视频源节点。自动抽取全部帧并入图片流水线; 配合 `推理模式=video` 使用时, 提示词优化前会先对视频整体反推 (采样≤8 帧)。与 images/image_N 同时连接时视频帧排在图片之后。旧工作流不受影响。

#### v1.4.8
- **新增视频反推**: 推理模式为 `video` 且连接多帧时, 提示词优化前先将输入帧视为**一段视频**整体反推 (均匀采样最多 8 帧, 单次调用描述主体动作/运镜/时间变化), 反推描述以 `[Reference Video]` 块注入优化请求; 上下文不足时自动 8→4→2 帧减帧重试, 最终兜底纯文本优化。图片模式逐张反推行为不变。
- **max_tokens 上限放开**: `Llama-cpp Parameters` 的 `max_tokens` 上限由 4096 提升至 32768。

#### v1.4.7
- **移除 `输出语言` 参数**: 模型经常无视系统提示词中的输出语言指令 (skill 规范本身是英文), 该控件无法可靠控制输出语言, 故删除。
  - 现在优化结果**固定为中英双语**: 英文版 (skill 规范原生语言, 遵循度最好) 用于主推理, 中文版由独立翻译 pass 生成、便于查看, 一并从 `optimized_prompt` 输出。
  - 翻译 pass 若因上下文不足失败, 自动降级为仅输出英文版, 不中断流程。
  > ⚠️ 参数移除会使旧工作流中该项设置失效 (节点结构不受影响)。若希望节省一次翻译推理只输出英文, 可再反馈加回开关。

#### v1.4.6
- **修复主推理 decode 溢出**: 解决 `Llama.eval(decode): Failed completely even with batch size 1.` (优化后长提示词 + 图片 + 输出 token 超出 n_ctx 导致 KV cache 写满)。
  - 主推理 (含 `one by one` 逐张模式) 同样按上下文预算选择图片边长, 溢出时逐级缩小重试 (1024→768→512→384→256)。
  - 新增**输出 token 预算收窄**: 按 `n_ctx - 提示词 - 余量` 自动降低 `max_tokens`, 避免生成阶段再次撑爆; 提示词不长时完全不改动。
  - 错误识别统一: `Multimodal chunk exceeded context limit` 与 `Failed completely even with batch size 1` 都判定为上下文类, 才触发降级; 其他错误 (如显存不足) 照常抛出。
  > 根本解法仍是调大 `Llama-cpp Model Loader` 的 `n_ctx` (多图 + Qwen 系建议 16384 以上), 降级只是保底。

#### v1.4.5
- **修复上下文溢出崩溃**: 解决 `Qwen35ChatHandler: Multimodal chunk exceeded context limit (n_ctx=8192)` 报错。提示词优化 pass 现按上下文预算自动选择参考图边长 (1024→768→512→384→256), 失败时逐级缩小重试; 仍放不下则退回纯文本优化 (保留反推描述); 单张反推失败会跳过而不中断整体流程。
  > 估算依据: 中日韩字符 ~1 token/字, 其余 ~4 字符/token, 视觉约 28px/token (Qwen-VL 系)。优化请求的 max_tokens 也会按剩余空间自动收窄, 避免输出阶段再次溢出。
  > 若仍报上下文不足, 请在 `Llama-cpp Model Loader` 节点调大 `n_ctx`, 或减少参考图数量 / 缩短提示词。

#### v1.4.4
- **用户意图优先**: 修复优化器忽略自定义提示词动作的问题 (如输入 "唱着歌曲" 但参考图是弹琵琶, 优化结果丢失唱歌)。优化请求现注入 [Priority Rule]: 用户提示词是首要创作意图, 其描述的动作/事件 (唱歌、跳舞、对话等) 即使参考图中不可见或与画面矛盾, 也必须保留在优化结果中; 参考图仅提供外观/服装/道具/场景/风格。
- **参数中文化**: `generation_mode` / `output_language` / `no_bgm` 更名为 `生成模式` / `输出语言` / `无背景音乐`。
  > ⚠️ 参数名变更会使旧工作流中这三项的已保存值重置为默认 (生成模式=None), 重新选择一次即可。

#### v1.4.3
- **移除提示词优化的后台打印**: 不再向控制台/后台输出优化后的完整提示词及各阶段进度日志 (优化结果仍从 `optimized_prompt` 输出口获取).
  > 仅保留一条提示: 当预设含 `*` 占位符 (检测类预设) 导致优化被跳过时会说明原因.

#### v1.4.2
- **提示词优化增强**: 选择 `generation_mode` 且连接参考图时, 优化前先逐张**反推**参考图内容, 反推描述与自定义提示词一并交给对应 skill 改写, 生成规范的编辑提示词 (自动将 "图1/图2" 等序数词引用映射为 `<image1>/<image2>` / `<Picture N>` 标准标签).
  > 示例: 输入 "图1的女人坐在图2的黄色沙发上" + 2 张参考图 → 优化器结合两张图的反推内容, 输出符合 Qwen-Image-2.1 编辑规范的提示词.

#### v1.4.1
- **精简节点**: 移除 `Llama-cpp Clean States` / `Llama-cpp Image Recognition` / `Llama-cpp Dynamic Image Switch` 及独立提示词优化节点 (功能已内置于 Instruct 节点).
  > 提示词优化请直接使用 `Llama-cpp Instruct` 节点的 `generation_mode` / `output_language` / `no_bgm` 参数, 优化结果从新增的 `optimized_prompt` 输出口获取.

#### v1.4.0
- **新增提示词优化**: Instruct 节点内置 MiniMax-H3 / Qwen-Image-2.1 专用提示词优化 (generation_mode, 默认 None 关闭), 支持中英文输出, 优化后的提示词通过新增的 `optimized_prompt` 输出口输出.
- **新增独立提示词优化节点** (`Llama-cpp Prompt Optimizer`): 仅优化不推理, 输出 english_prompt / chinese_prompt.
- 参考 [ComfyUI-xiaozhuguang](https://github.com/xiaozhuguang/ComfyUI-xiaozhuguang) (MIT) 移植.

#### v1.2.9
- 新增 Qwen3.8 / Qwen3.8-Thinking 支持 (含 27B), 支持思考模式开关; 旧版 llama-cpp-python 自动回退到 Qwen35 兼容处理器.
  > 注意: Qwen3.8 的模型架构需要 2026-08-14 之后构建的 llama.cpp / llama-cpp-python, 请安装最新的 [JamePeng 轮子](https://github.com/JamePeng/llama-cpp-python/releases)或自行编译.
- 修复动态图片接口: 拔掉 image_2 后不再错误出现 image_3; 增删接口不再导致节点 UI 变窄; 自动清理旧工作流遗留的 image / queue_handler 接口.
- 移除 queue_handler 接口.
- 新增自动卸载显存/内存: 其他模型加载到 GPU 时, 剩余显存低于阈值 (加载器节点可调, 默认 2GB) 自动卸载 LLM.

## 致谢
- [llama-cpp-python](https://github.com/JamePeng/llama-cpp-python) @JamePeng  
- [ComfyUI-llama-cpp](https://github.com/kijai/ComfyUI-llama-cpp) @kijai
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) @comfyanonymous
