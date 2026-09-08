import { app } from "../../scripts/app.js";

const IMAGE_INPUTS = [
    "image_1", "image_2", "image_3", "image_4", "image_5",
    "image_6", "image_7", "image_8", "image_9", "image_10"
];
const MAX_IMAGE_INPUTS = IMAGE_INPUTS.length;
const LITEGRAPH_INPUT = (typeof LiteGraph !== "undefined" && LiteGraph.INPUT) || 1;

function isImageInput(inp) {
    return !!inp && IMAGE_INPUTS.includes(inp.name);
}

function hasLink(inp) {
    return inp.link !== null && inp.link !== undefined;
}

/**
 * 统一校正 image 输入槽, 保证以下不变量 (connect / disconnect / 加载工作流后都收敛到同一状态):
 *   1. image_1 始终存在;
 *   2. 所有已连接的 image 槽全部保留;
 *   3. 最后一个已连接槽之后恰好保留一个空槽 (供继续接入下一张图);
 *   4. 多余的空槽一律移除 —— 修复"拔掉 image_2 却冒出 image_3"的问题;
 *   5. image 槽整体保持编号顺序, 且位于 queue_handler 之前 (addInput 默认追加到末尾的问题一并修复).
 */
function refreshImageInputs(node) {
    if (!node || !node.inputs || node._refreshingImageInputs) return;
    node._refreshingImageInputs = true;
    try {
        // 清理旧版本节点遗留的未连接 "image" / "queue_handler" 槽 (兼容老工作流)
        for (let i = node.inputs.length - 1; i >= 0; i--) {
            const inp = node.inputs[i];
            if (inp && (inp.name === "image" || inp.name === "queue_handler") && !hasLink(inp)) {
                node.removeInput(i);
            }
        }

        // 已连接的 image 槽中最大的编号 (1-based)
        let maxConnected = 0;
        for (const inp of node.inputs) {
            if (isImageInput(inp) && hasLink(inp)) {
                maxConnected = Math.max(maxConnected, IMAGE_INPUTS.indexOf(inp.name) + 1);
            }
        }
        // 期望可见槽数: 最后已连接编号 + 1 个空槽, 至少保留 image_1
        const want = Math.min(Math.max(maxConnected + 1, 1), MAX_IMAGE_INPUTS);

        // 1) 从后往前删除超出范围的未连接槽 (绝不删带连接的槽, 防止丢线)
        for (let i = node.inputs.length - 1; i >= 0; i--) {
            const inp = node.inputs[i];
            if (!isImageInput(inp)) continue;
            const num = IMAGE_INPUTS.indexOf(inp.name) + 1;
            if (num > want && !hasLink(inp)) {
                node.removeInput(i);
            }
        }

        // 2) 补齐 1..want 中缺失的槽
        for (let num = 1; num <= want; num++) {
            const name = IMAGE_INPUTS[num - 1];
            if (!node.inputs.some((inp) => inp.name === name)) {
                const cfg = node._imageInputConfigs?.[name] || {};
                node.addInput(name, cfg.type || "IMAGE", { label: cfg.label, tooltip: cfg.tooltip });
            }
        }

        // 3) 排序: image 槽按编号连续排列, 并整体移动到 queue_handler 之前
        const imageInputs = node.inputs
            .filter(isImageInput)
            .sort((a, b) => IMAGE_INPUTS.indexOf(a.name) - IMAGE_INPUTS.indexOf(b.name));
        const others = node.inputs.filter((inp) => !isImageInput(inp));
        const qhIdx = others.findIndex((inp) => inp.name === "queue_handler");
        if (qhIdx !== -1) {
            others.splice(qhIdx, 0, ...imageInputs);
        } else {
            others.push(...imageInputs);
        }
        node.inputs.length = 0;
        node.inputs.push(...others);

        // 只调整高度, 保留用户设置的宽度 (避免增删槽位后 UI 变窄)
        if (node.computeSize && node.setSize) {
            const minSize = node.computeSize();
            const curW = (node.size && node.size[0]) || minSize[0];
            node.setSize([Math.max(curW, minSize[0]), minSize[1]]);
        }
        node.graph?.setDirtyCanvas?.(true, true);
    } finally {
        node._refreshingImageInputs = false;
    }
}

/**
 * 延迟一帧再校正: 部分前端版本在 onConnectionsChange 回调时 link 状态尚未更新,
 * 推迟到事件循环下一拍可保证读到最终的连接状态, 同时合并连续触发的多次事件.
 */
function scheduleRefresh(node) {
    if (node._imageRefreshScheduled) return;
    node._imageRefreshScheduled = true;
    setTimeout(() => {
        node._imageRefreshScheduled = false;
        try {
            if (!node.graph) return; // 节点已被移除
            refreshImageInputs(node);
        } catch (e) {
            console.warn("[llama_cpp_vlm] refresh image inputs failed:", e);
        }
    }, 0);
}

app.registerExtension({
    name: "ComfyUI.llama_cpp_vlm.dynamic_image_inputs",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "llama_cpp_instruct_adv") return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            // 保存所有 image 输入的原始配置 (用于后续动态补槽)
            this._imageInputConfigs = {};
            for (const inp of this.inputs || []) {
                if (isImageInput(inp)) {
                    this._imageInputConfigs[inp.name] = {
                        name: inp.name,
                        type: inp.type,
                        label: inp.label,
                        tooltip: inp.tooltip,
                    };
                }
            }
            // 初始只保留 image_1
            refreshImageInputs(this);
        };

        const onConnectionsChange = nodeType.prototype.onConnectionsChange;
        nodeType.prototype.onConnectionsChange = function (type, slotIndex, isConnected, link, ioSlot) {
            const r = onConnectionsChange?.apply(this, arguments);
            if (type !== LITEGRAPH_INPUT) return r;
            const inp = this.inputs?.[slotIndex];
            if (inp && (isImageInput(inp) || inp.name === "image")) {
                // 断开时防御性地清空该槽 link, 兼容 link 后置清空的时序
                if (!isConnected) inp.link = null;
                scheduleRefresh(this);
            } else if (!inp) {
                // 槽位索引已变化 (例如刚删除过槽), 也做一次校正
                scheduleRefresh(this);
            }
            return r;
        };

        // 加载工作流后按实际连接状态重建槽位
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function () {
            const r = onConfigure?.apply(this, arguments);
            scheduleRefresh(this);
            return r;
        };
    }
});
