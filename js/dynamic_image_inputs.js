import { app } from "../../scripts/app.js";

const IMAGE_INPUTS = [
    "image_1", "image_2", "image_3", "image_4", "image_5",
    "image_6", "image_7", "image_8", "image_9", "image_10"
];

app.registerExtension({
    name: "ComfyUI.llama_cpp_vlm.dynamic_image_inputs",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "llama_cpp_instruct_adv") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            // 保存所有 image 输入的原始配置
            this._imageInputConfigs = {};
            for (const inp of this.inputs) {
                if (IMAGE_INPUTS.includes(inp.name)) {
                    this._imageInputConfigs[inp.name] = {
                        name: inp.name,
                        type: inp.type,
                        label: inp.label,
                        tooltip: inp.tooltip,
                    };
                }
            }

            // 初始只保留 image_1，删除 image_2 ~ image_10
            for (let i = this.inputs.length - 1; i >= 0; i--) {
                const idx = IMAGE_INPUTS.indexOf(this.inputs[i].name);
                if (idx > 0) {
                    this.removeInput(i);
                }
            }
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (type, slotIndex, isConnected, link, ioSlot) {
            onConnectionsChange?.apply(this, arguments);

            if (type !== LiteGraph.INPUT) return;

            const input = this.inputs[slotIndex];
            if (!input || !IMAGE_INPUTS.includes(input.name)) return;

            const imageInputs = this.inputs.filter(inp => IMAGE_INPUTS.includes(inp.name));
            const lastImageInput = imageInputs[imageInputs.length - 1];
            const lastIdx = IMAGE_INPUTS.indexOf(lastImageInput.name);

            if (isConnected) {
                // 最后一个 image 输入已连接时，添加下一个
                if (lastImageInput.link != null && lastImageInput.link !== undefined) {
                    const nextName = IMAGE_INPUTS[lastIdx + 1];
                    if (nextName && this._imageInputConfigs[nextName]) {
                        const cfg = this._imageInputConfigs[nextName];
                        this.addInput(cfg.name, cfg.type, { label: cfg.label, tooltip: cfg.tooltip });
                    }
                }
            } else {
                // 断开时，从后往前移除所有未连接的额外 image 输入（保留 image_1）
                for (let i = this.inputs.length - 1; i >= 0; i--) {
                    const inp = this.inputs[i];
                    const idx = IMAGE_INPUTS.indexOf(inp.name);
                    if (idx <= 0) continue; // 不删 image_1
                    if (inp.link == null || inp.link === undefined) {
                        this.removeInput(i);
                    } else {
                        break; // 遇到已连接的就停止
                    }
                }
            }
        };
    }
});
