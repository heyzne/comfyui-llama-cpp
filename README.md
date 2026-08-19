# ComfyUI-llama-cpp

Run LLM & VLM models natively in ComfyUI based on the llama.cpp framework.  
**[[📃中文说明](./README_zh.md)]**

## Preview
最多可输入6张反推图片
## Installation

#### Install Nodes:
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/heyzne/comfyui-llama-cpp.git
python -m pip install -r ComfyUI-llama-cpp/requirements.txt
```

### Model Path:
- Place downloaded `.gguf` models in the `ComfyUI/models/LLM` directory.

> Before using VLM models for image inference, make sure you have downloaded and selected the `mmproj` weight file corresponding to the main model.

## Features

- **LLM Text Generation** — Run any GGUF language model for text completion and chat
- **VLM Vision Understanding** — Support for LLaVA 1.5/1.6, Moondream2, nanoLLaVA, Llama3-Vision-Alpha, MiniCPM-v2.6/v4.5, Gemma3/4, Qwen2.5-VL, Qwen3-VL, Qwen3.5, GLM-4.1V/4.6V, LFM2-VL/LFM2.5-VL, Granite-Docling
- **Image Recognition** — Dynamic image input recognition with multiple presets (Describe, Tags, Objects, Scene, OCR, etc.)
- **Dynamic Image Switch** — Auto-detect image input and switch between text-only and vision modes
- **Bounding Box Detection** — JSON-based object detection with bbox output compatible with ComfyUI's BBOX/SEGS/MASK pipeline
- **Video Understanding** — Process image sequences as video frames for video understanding
- **Prompt Enhancement** — Built-in prompt enhancer presets for Qwen-Image, Flux.2, Wan, Z-Image Turbo, and more
- **Multi-Platform** — Supports Windows (CUDA), Linux (CUDA), and macOS (Metal)
- **VRAM Control** — Adjustable GPU layer count for VRAM-constrained environments

## Nodes

| Node | Description |
|------|-------------|
| `Llama-cpp Model Loader` | Load GGUF models with optional mmproj for vision |
| `Llama-cpp Instruct` | Main inference node with multi-image, video, and conversation support |
| `Llama-cpp Parameters` | Configure generation parameters (temperature, top-p, etc.) |
| `Llama-cpp Image Recognition` | Recognize images with preset modes (Describe, Tags, OCR, etc.) |
| `Llama-cpp Dynamic Image Switch` | Auto-detect images and switch between text/vision modes |
| `Llama-cpp Unload Model` | Manually unload model to free VRAM |
| `Llama-cpp Clean States` | Clear saved conversation states |
| `Parse JSON` | Parse JSON strings with key extraction |
| `JSON to BBoxes` | Convert JSON detection results to BBOX format |
| `BBoxes to SEGS` | Convert BBOX to ComfyUI SEGS format |
| `BBoxes to MASK` | Convert BBOX to ComfyUI MASK format |
| `BBoxes to BBox` | Extract individual bbox from list |
| `Unpack Code Block` | Remove markdown code block formatting |
| `Prompt Enhancer Preset` | System prompt presets for various image/video generation models |

## Supported Chat Handlers

- LLaVA-1.5 / LLaVA-1.6
- Moondream2
- nanoLLaVA
- Llama3-Vision-Alpha
- MiniCPM-v2.6 / MiniCPM-v4.5 / MiniCPM-v4.5-Thinking
- Gemma3 / Gemma4
- Qwen2.5-VL / Qwen3-VL / Qwen3-VL-Thinking
- Qwen3.5 / Qwen3.5-Thinking
- Qwen3.8
- GLM-4.1V-Thinking / GLM-4.6V / GLM-4.6V-Thinking
- LFM2-VL / LFM2.5-VL
- Granite-Docling

## Acknowledgments
- [llama-cpp-python](https://github.com/JamePeng/llama-cpp-python) @JamePeng
- [ComfyUI-llama-cpp](https://github.com/kijai/ComfyUI-llama-cpp) @kijai
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) @comfyanonymous
