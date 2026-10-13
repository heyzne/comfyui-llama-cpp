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
