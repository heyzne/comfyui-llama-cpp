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
