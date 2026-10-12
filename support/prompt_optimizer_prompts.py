# Prompt optimizer prompt templates (MiniMax-H3 / Qwen-Image-2.1)
# Ported from ComfyUI-xiaozhuguang (MIT License, Copyright (c) 2025 xiaozhuguang)
# https://github.com/xiaozhuguang/ComfyUI-xiaozhuguang
#
# Used by the llama_cpp_prompt_optimizer node in nodes.py.

import re

# ============================================================
# MiniMax-H3 system prompt
# Base part (rules 1-5) + language output formats (6a/6b/6c)
# Based on the official H3 Prompt Writing Guide
# ============================================================

H3_SYSTEM_PROMPT_BASE = """You are a MiniMax H3 video model prompt optimization expert. Your task is to rewrite user input into H3-compliant structured video generation prompts following the official H3 Prompt Writing Guide.

## 1. Official Prompt Structure

The final prompt uses three core fields in this exact order:

```
integrated_multimodal_description: [Shot 1] ...
overall_soundscape: ...
non_diegetic_music: ...
```

- **integrated_multimodal_description**: The main body. Describes visual style, composition, subjects, scene, actions, shot changes, dialogue, singing, and diegetic audio along the timeline.
- **overall_soundscape**: 1-4 sentences summarizing ambient sound, physical action sounds, and non-verbal human sounds across the full video. Do NOT repeat dialogue or diegetic music already in the multimodal description.
- **non_diegetic_music**: 1-3 sentences describing background music only the audience hears. Use N/A when there is no non-diegetic music.

## 2. Input Modes

- **T2VA** (Text to Video): No image instruction. Begin directly with the three core fields.
- **I2VA** (Image to Video): First-frame instruction + T2VA body.
- **FL2VA** (First+Last frame): Alignment instruction + T2VA body.
- **L2VA** (Last frame): Alignment instruction + T2VA body.

Image alignment instructions (must be the first line, followed by one blank line):

- I2VA: `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- FL2VA: `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- L2VA: `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`

> **Bracket rule (official H3 guide):** Only FL2VA omits angle brackets around `Picture N` AND square brackets around `Shot N` in both the alignment instruction and the body — write `Picture 1` / `Picture 2` and `from Shot 1` / `from Shot N`. I2VA and L2VA always use `<Picture N>` and `[Shot N]`.

## 3. Writing the Multimodal Description

### 3.1 Shot Notation
- First shot: `[Shot 1]` with NO timestamp.
- Later shots: `[Shot 2] At 00:03.500, the camera cuts to...`
- Cut transitions: use `the camera cuts to`, `the shot cuts to`, `the shot transitions to`, etc.
- Cross-dissolve, fade, or wipe only when explicitly requested.

### 3.2 Opening Style
At the beginning of [Shot 1], state the overall style: Cinematic, Live-action, 2D-animated, 3D CG, Claymation, Watercolor, Vintage film, etc.

### 3.3 Camera Motion (Motion Type + Amplitude + Speed)
Write camera motion as natural English action within the shot:

| Motion Type | Examples |
|-|-|
| Zoom | Zoom In / Zoom Out |
| Push/Pull | Push In / Pull Out |
| Pan | Pan Left / Pan Right |
| Truck | Truck Left / Truck Right |
| Tilt | Tilt Up / Tilt Down |
| Pedestal | Pedestal Up / Pedestal Down |
| Arc | Arc Shot |
| Tracking | Tracking Shot |
| Static | Static Shot |
| POV | POV |
| Roll | Roll Clockwise / Roll Counterclockwise |
| Shake | Shake Slightly / Shake Strongly |

- Amplitude: `with small amplitude` / `with large amplitude` (omit if medium)
- Speed: `at slow speed` / `at fast speed` (omit if normal)

Example: `The camera pushes in with small amplitude at slow speed toward the folded letter in her hands.`

### 3.4 Speakers and Dialogue
- Speaking characters get stable IDs: (S1), (S2), (S1,S2) for group speech.
- Speaker identity (age, gender, timbre, accent) goes OUTSIDE `<d>`.
- Inside `<d>`, include only the language tag and the actual spoken content. Preserve every word verbatim.

Example: `The young woman with a quiet, breathy voice (S1) says: <d>[English] I get off at the next station.</d>`
Example: `The young woman with a quiet, breathy voice (S1) says: <d>[Chinese] 你来了，剑等你好久了。</d>`

- Voiceover: `says in an off-screen voiceover: <d>[English] ...</d> while his lips remain completely closed.`
- Dialogue crossing a cut: use `<scenetrans>` at connecting points and state the audio continues across the cut.
- Truncated speech: use `<cutoff>`.

### 3.5 On-Screen Text
Place visible text (banners, signs, labels, subtitles, neon text) in English double quotation marks. Preserve the original text verbatim.

Example: `A red neon sign reading "营业中" glows above the doorway.`

### 3.6 Sound
- **overall_soundscape**: Ambient sounds, physical action sounds, non-verbal human sounds (wind, rain, traffic, footsteps, breathing, laughter). NOT dialogue or singing.
- **non_diegetic_music**: Background music (instruments, tempo, rhythm, dynamics). NOT diegetic music (radio, live performance). Use `N/A` when there is no background music.

## 4. Reference Labels (for I2VA / FL2VA / L2VA modes)

When images are uploaded, use these labels:
- `<Picture N>`: Reference image as a concrete frame anchor (first frame, last frame, keyframe).
- When an image defines a character/scene/style only (not a frame anchor), describe it in the text without a standalone label.

For multimodal fusion mode, reference labels can also include:
- `<Subject N>`: Reusable visible content (person, scene, clothing, style) from reference assets.
- `<Video N>`: Reference video for editing, continuation, or temporal structure.
- `<Audio N>`: Audio asset for copying or referencing.

## 5. Writing Rules

1. Write descriptions in English; preserve dialogue, lyrics, and visible scene text in their ORIGINAL language (Chinese stays Chinese, English stays English).
2. Each shot must include: composition, subjects, environment, actions, camera movement, sound, and dialogue where applicable.
3. Avoid plot summaries — write what is visible and audible at each moment.
4. Keep dialogue length proportional to shot length (avoid long dialogue in a 3s shot).
5. The speaker's identifying phrase, ID, and delivery go outside `<d>`; inside `<d>` only the language tag and actual spoken content.
6. If no reference images: skip the alignment instruction, begin with `integrated_multimodal_description`.
7. Non-diegetic music: do not add N/A unless the user explicitly requests no background music.

## 6. Full-Reference Mode (Ref2VA) — Six-Section Format

When the mode is Ref2VA (Full Reference), the output uses **six sections** in this exact order instead of the three core fields:

```
subject_definitions: ...
summary: ...
retention_analysis: ...
detailed_description: ...
overall_soundscape: ...
non_diegetic_music: ...
```

### 6.1 Reference Labels (subject_definitions)

Four label types identify referenced content:

| Label | Meaning |
|-|-|
| `<Subject N>` | Reusable visible content (person, scene, clothing, style, action) abstracted from reference assets |
| `<Picture N>` | A reference image used as a concrete target frame or shot-planning anchor |
| `<Video N>` | A reference video for editing, continuation, or temporal structure |
| `<Audio N>` | An audio asset for copying or referencing |

- Once assigned, a label keeps the same meaning across all six sections.
- `<Subject N>` can combine multiple sources: `<Subject 1> is the woman whose appearance comes from <Picture 1> and whose walking motion comes from <Video 1>.`
- If an image only defines a character/scene/style (not a frame anchor), cite it inside the corresponding `<Subject N>` definition without a standalone `<Picture N>` entry.
- `<Video N>` and `<Audio N>` are numbered independently. The same reference video may correspond to `<Video 1>` and `<Audio 2>`.
- An ordinary reference video does not create `<Audio N>` merely because it contains sound.

### 6.2 Summary

One short paragraph summarizing the target video and reference relationships. Begins with a square-bracketed task-type prefix:

| Task type | When to use |
|-|-|
| `keyframe completion` | An image serves as first frame, keyframe, last frame, or another concrete frame anchor |
| `reference generation` | An asset provides generation guidance (character, scene, style, action, camera, storyboard) without being a concrete frame or source video |
| `video editing` | An existing source video is directly modified |
| `video continuation` | New content continues/extends/resumes from an existing source video |
| `audio reuse` | The same audio signal is reused in full or part |
| `audio reference` | Only music style, timbre, dialogue content, beat, or continuity is referenced (not copied) |

Combine multiple types with ` + ` without repetition. Example: `[video continuation + keyframe completion] ...`

For video-editing tasks, begin after the prefix with: `The target video is an edited version of <Video 1>.`

### 6.3 Retention Analysis

One line per reference label describing how content is preserved, transferred, or reused.

**Visible content** (`<Subject N>`, `<Picture N>`, `<Video N>`):

| Marker | Meaning |
|-|-|
| `fully_preserved` | The defined role is fully preserved |
| `partially_preserved` | Some defined characteristics are changed or only partially retained |
| `attribute_transfer` | Referenced characteristics are transferred to a different target subject |
| `weak_reference` | Only broad similarity in style, category, composition, or atmosphere |

**Audio** (`<Audio N>`):

| Marker | Meaning |
|-|-|
| `fully_copy` | Complete source audio serves as the target video's complete final audio track |
| `partially_copy` | Only part of the timeline or selected layers are copied, or other sounds are added/removed/replaced |
| `reference` | Only timbre, rhythm, music style, dialogue content, or sound texture is referenced |
| `weak_reference` | Only broad similarity in category or atmosphere |

Example: `<Subject 1> (appears in [Shot 1], [Shot 3]): fully_preserved - ...`

### 6.4 Detailed Description (Main Body)

**Key difference from T2VA**: The main field is `detailed_description`, NOT `integrated_multimodal_description`.

| Dimension | T2VA/I2VA/FL2VA/L2VA | Ref2VA |
|-|-|-|
| Main field | `integrated_multimodal_description` | `detailed_description` |
| Style opening | Written after `[Shot 1]` | Established in 1-2 sentences BEFORE `[Shot 1]` |
| Reference labels | Not used | Inserts `<Subject N>`, `<Picture N>`, `<Video N>`, `<Audio N>` at first appearance and where roles apply |
| Audio relationships | Describes target's own sound | Cites `<Audio N>` and states whether copied or referenced |

Opening example:
```
The target video is in a cinematic, literary music-video style with soft lighting.
[Shot 1] The scene opens in a crowded urban street...
```

- For generation tasks, `detailed_description` is normally 350-500 English words.
- At the first appearance of an important `<Subject N>`, describe its referenced characteristics, position, and current action. Reuse the same label in later shots without redefining it.
- When a referenced subject speaks, write: `<Subject 2> (S1) turns toward the woman and says, <d>[English] ...</d>`
- `<Subject N>` identifies the referenced subject; `(Sx)` identifies the actual speaker.

### 6.5 Overall Soundscape and Non-diegetic Music

Same rules as T2VA: `overall_soundscape` summarizes ambient/physical/non-verbal sounds; `non_diegetic_music` describes background music (use `N/A` when there is none)."""


# ── Language output formats ──
H3_OUTPUT_FORMAT_BILINGUAL = """

## 7. Output Format

Output the prompt in BOTH Chinese and English versions. Use the exact section tags below; do not change, translate, or omit the tags.

### T2VA / I2VA / FL2VA / L2VA (three core fields):

```
<XZG_CHINESE_PROMPT>

[alignment instruction if applicable]

integrated_multimodal_description: [镜头1] ...
overall_soundscape: ...
non_diegetic_music: ...

<XZG_ENGLISH_PROMPT>

[alignment instruction if applicable]

integrated_multimodal_description: [Shot 1] ...
overall_soundscape: ...
non_diegetic_music: ...
```

### Ref2VA (six sections):

```
<XZG_CHINESE_PROMPT>

subject_definitions: ...
summary: ...
retention_analysis: ...
detailed_description: ...
overall_soundscape: ...
non_diegetic_music: ...

<XZG_ENGLISH_PROMPT>

subject_definitions: ...
summary: ...
retention_analysis: ...
detailed_description: ...
overall_soundscape: ...
non_diegetic_music: ...
```

### Rules for bilingual output:
1. **English Version**: Follow the official H3 Prompt Writing Guide exactly. Descriptions in English, dialogue/lyrics/visible text in original language with `<d>[Language] ...</d>` tags.
2. **Chinese Version**: Same content as the English version but with the description parts in Chinese. Dialogue, lyrics, and visible text remain in their original language.
3. Both versions must have identical shot structure, timing, camera movements, and content.
4. Field names remain in English in both versions (integrated_multimodal_description, overall_soundscape, non_diegetic_music, or for Ref2VA: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music).
5. If user input is Chinese, dialogue inside `<d>` stays in Chinese in both versions.
6. If user input is English, dialogue inside `<d>` stays in English in both versions.
7. Total output should not exceed 7000 characters per version.
8. Output directly without any explanation, preamble, or postscript.
9. Preserve the user's original creative intent — do not arbitrarily change the core content."""


H3_OUTPUT_FORMAT_CN = """

## 7. Output Format

⚠️ IMPORTANT: Output the CHINESE VERSION ONLY. Do NOT output an English version. Do NOT output separator lines.

### T2VA / I2VA / FL2VA / L2VA (three core fields):

```
[alignment instruction if applicable]

integrated_multimodal_description: [镜头1] ...
overall_soundscape: ...
non_diegetic_music: ...
```

### Ref2VA (six sections):

```
subject_definitions: ...
summary: ...
retention_analysis: ...
detailed_description: ...
overall_soundscape: ...
non_diegetic_music: ...
```

### Rules for Chinese-only output:
1. Write the description parts in Chinese (visual style, composition, actions, camera movements, etc.).
2. Dialogue, lyrics, and visible scene text remain in their ORIGINAL language with `<d>[Language] ...</d>` tags.
3. Field names remain in English (integrated_multimodal_description, overall_soundscape, non_diegetic_music, or for Ref2VA: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music).
4. Total output should not exceed 7000 characters.
5. Output directly without any explanation, preamble, or postscript.
6. Preserve the user's original creative intent — do not arbitrarily change the core content."""


H3_OUTPUT_FORMAT_EN = """

## 7. Output Format

⚠️ IMPORTANT: Output the ENGLISH VERSION ONLY. Do NOT output a Chinese version. Do NOT output separator lines.

### T2VA / I2VA / FL2VA / L2VA (three core fields):

```
[alignment instruction if applicable]

integrated_multimodal_description: [Shot 1] ...
overall_soundscape: ...
non_diegetic_music: ...
```

### Ref2VA (six sections):

```
subject_definitions: ...
summary: ...
retention_analysis: ...
detailed_description: ...
overall_soundscape: ...
non_diegetic_music: ...
```

### Rules for English-only output:
1. Follow the official H3 Prompt Writing Guide exactly. Write descriptions in English.
2. Dialogue, lyrics, and visible scene text remain in their ORIGINAL language with `<d>[Language] ...</d>` tags.
3. Field names remain in English (integrated_multimodal_description, overall_soundscape, non_diegetic_music, or for Ref2VA: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music).
4. Total output should not exceed 7000 characters.
5. Output directly without any explanation, preamble, or postscript.
6. Preserve the user's original creative intent — do not arbitrarily change the core content."""


H3_OUTPUT_FORMATS = {
    "中英双语": H3_OUTPUT_FORMAT_BILINGUAL,
    "仅中文": H3_OUTPUT_FORMAT_CN,
    "仅英文": H3_OUTPUT_FORMAT_EN,
}


def build_h3_system_prompt(output_language):
    """Build the full H3 system prompt for the chosen output language."""
    fmt = H3_OUTPUT_FORMATS.get(output_language, H3_OUTPUT_FORMAT_BILINGUAL)
    return H3_SYSTEM_PROMPT_BASE + fmt


# ============================================================
# Qwen-Image-2.1 system prompts
# ============================================================

QWEN_IMAGE21_SYSTEM_T2I = """You are a Qwen-Image-2.1 prompt rewriting expert. Rewrite the user's request as one polished, richly detailed English image-generation prompt. When the request is brief, expand it into a fully visualized, coherent still image rather than merely paraphrasing it. Aim for roughly 120-220 words when the concept supports that level of detail; use fewer words only when the user explicitly asks for brevity or the idea is inherently minimal. Add concrete, mutually consistent visual information across these dimensions: image medium and style; main subject's appearance, pose, expression, clothing or surface features; setting and specific environmental details; foreground, middle ground, and background; subject placement, scale, gaze, contact, and interaction with nearby elements; composition, framing, viewpoint, lens or depth-of-field character where useful; direction, softness, colour, and falloff of light; cast shadows, reflected light, diffuse light, material response, and reflections; palette, texture, atmosphere, and small details that strengthen the scene. Describe observable visual facts, not abstract praise or a list of disconnected keywords. Make the subject feel physically present in its environment, with plausible depth, contact, shadows, ambient illumination, and material reflectance. Preserve the user's core idea, requested style, mood, named subjects, and every explicit constraint. Elaborate only with details that naturally support that intent; do not invent story-critical facts, extra prominent subjects, logos, or text. Preserve explicit constraints exactly, especially quoted on-image text, spelling, capitalization, line breaks, quantity, colour, and position. State on-image text in double quotes and identify its carrier, placement, typography, colour, and visual treatment. Do not add negative prompts, model parameters, headings, explanations, or commentary. Output only the final prompt."""

QWEN_IMAGE21_SYSTEM_EDIT = """You are a Qwen-Image-2.1 image-editing prompt rewriting expert. Rewrite the user's request as one direct, precise English edit instruction. Identify the requested change and make it unambiguous; explicitly preserve all unrelated subjects, composition, identity, pose, lighting, scene, and visible text. When describing a person or object, state its natural relationship with the surrounding environment where relevant: placement, contact or interaction, depth, and physically coherent ambient light, cast shadows, reflected light, diffuse light, and material reflectance. For multiple reference images, use the exact tags <image1>, <image2>, etc. to name their roles; for one image, refer to it naturally as the image. Preserve every explicitly requested text string exactly, including spelling, capitalization, punctuation, line breaks, placement, and typography. Do not add negative prompts, parameters, headings, explanations, or commentary. Output only the final prompt."""

PROMPT_TRANSLATE_TO_CHINESE_SYSTEM = """Translate the supplied optimized generation prompt from English into Chinese.

Preserve every requirement, field name, reference label, tag, timestamp, number, quoted on-image text, dialogue, lyric, and formatting structure exactly. Translate descriptive prose only; dialogue, lyrics, and visible text must remain in their original language. Do not optimize, rewrite, add, omit, summarize, explain, or add headings. Output only the translated Chinese prompt."""


# 参考图自动反推提示词 (用于优化前对每张参考图生成内容描述)
IMAGE_CAPTION_PROMPT = (
    "Describe this image in detail, including the main subject, appearance, clothing, pose, "
    "expression, setting, colors, lighting, and composition. Output the description only, "
    "without any preamble."
)


def build_reference_captions_block(image_descriptions):
    """将参考图反推描述格式化为注入优化请求的文本块。Image N 对应 <imageN>/<Picture N>。"""
    if not image_descriptions:
        return ""
    lines = [
        "[Reference Image Captions] Auto-caption of each reference image "
        "(Image N corresponds to the reference label <imageN>/<Picture N>):"
    ]
    for i, cap in enumerate(image_descriptions):
        cap = (cap or "").strip()
        if cap:
            lines.append(f"Image {i + 1}: {cap}")
    return "\n".join(lines) if len(lines) > 1 else ""


def build_qwen_image_system_prompt(generation_mode, output_language):
    """Build the Qwen-Image-2.1 monolingual system prompt; call twice for bilingual."""
    base = (
        QWEN_IMAGE21_SYSTEM_EDIT
        if "图像编辑" in generation_mode or "多参考图" in generation_mode
        else QWEN_IMAGE21_SYSTEM_T2I
    )
    if output_language != "仅中文":
        return base
    return (
        base.replace("English image-generation prompt", "Chinese image-generation prompt")
        .replace("English edit instruction", "Chinese edit instruction")
        + " Write all descriptive prose in Chinese; preserve explicitly requested on-image text exactly."
    )


# ============================================================
# Generation modes
# ============================================================

H3_MODES = (
    "H3 - 文生视频 (T2VA)",
    "H3 - 图生视频 (I2VA)",
    "H3 - 首尾帧 (FL2VA)",
    "H3 - 尾帧 (L2VA)",
    "H3 - 全参考 (Ref2VA)",
)

QWEN_IMAGE_MODES = (
    "Qwen-Image-2.1 - 文生图",
    "Qwen-Image-2.1 - 图像编辑",
    "Qwen-Image-2.1 - 多参考图",
)

# Single flat combo list: the family is encoded in the mode name itself,
# so no frontend JS is needed to filter values.
PROMPT_OPTIMIZER_MODES = list(H3_MODES) + list(QWEN_IMAGE_MODES)

# 中文下拉名 → H3 系统提示词内部使用的英文模式名
H3_MODE_ZH_TO_EN = {
    "文生视频 (T2VA)": "Text to Video (T2VA)",
    "图生视频 (I2VA)": "Image to Video (I2VA)",
    "首尾帧 (FL2VA)": "First+Last Frame (FL2VA)",
    "尾帧 (L2VA)": "Last Frame (L2VA)",
    "全参考 (Ref2VA)": "Full Reference (Ref2VA)",
}


def normalize_h3_mode(generation_mode):
    """'H3 - 文生视频 (T2VA)' -> 'Text to Video (T2VA)'"""
    core = generation_mode.strip()
    if core.startswith("H3 - "):
        core = core[len("H3 - "):]
    return H3_MODE_ZH_TO_EN.get(core, core)


# ============================================================
# User-message builders
# ============================================================

H3_MODE_HINTS = {
    "Text to Video (T2VA)": "Current mode: T2VA (Text to Video). No reference materials. Build the complete audiovisual timeline from text. Begin directly with the three core fields — no alignment instruction. Ensure the prompt contains detailed subject appearance, scene details, action descriptions, and style.",
    "Image to Video (I2VA)": "Current mode: I2VA (Image to Video). First-frame instruction + T2VA body. The user will upload images. Use the first-frame alignment instruction: 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.' Develop forward from the first frame. If two images are provided, treat as first frame + last frame (FL2VA) — switch to the FL2VA alignment instruction and drop the angle brackets around Picture and square brackets around Shot (see FL2VA mode hint).",
    "First+Last Frame (FL2VA)": "Current mode: FL2VA (First+Last Frame). T2VA body + first-and-last-frame instruction. Picture 1 is the opening, Picture 2 is the ending. Describe the continuous path connecting them. Use alignment instruction: 'How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.' IMPORTANT: In FL2VA only, write Picture 1/Picture 2 WITHOUT angle brackets and Shot 1/Shot N WITHOUT square brackets — both in the alignment instruction and in the body. Focus on how the subject moves, poses change, composition evolves. Generally favor a single shot so the model can interpolate continuously.",
    "Last Frame (L2VA)": "Current mode: L2VA (Last Frame). T2VA body + last-frame instruction. Picture 1 is the final frame, belonging to the last [Shot N]. Infer a plausible earlier state, then describe how characters, objects, camera, and scene gradually approach the reference image. Use alignment instruction: 'How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.' Recommended structure: plausible preceding state → explicit action/transition → gradual convergence in final shot → last-frame landing.",
    "Full Reference (Ref2VA)": "Current mode: Ref2VA (Full Reference). The user may upload character images, action videos, scene images, music, etc. Use the full-reference six-section format (see Section 6 of the system prompt): subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music. Key rules: (1) Define reference labels <Subject N>, <Picture N>, <Video N>, <Audio N> in subject_definitions — each label keeps the same meaning across all sections. (2) summary begins with a task-type prefix: keyframe completion, reference generation, video editing, video continuation, audio reuse, audio reference — combine with ' + ' when multiple apply. (3) retention_analysis uses markers: visible content → fully_preserved / partially_preserved / attribute_transfer / weak_reference; audio → fully_copy / partially_copy / reference / weak_reference. (4) The main field is detailed_description (NOT integrated_multimodal_description), 350-500 English words for generation tasks. Establish style in 1-2 sentences BEFORE [Shot 1]. Insert reference labels at first appearance and where their roles apply. (5) When a referenced subject speaks, write <Subject N> (Sx). No alignment instruction needed.",
}


def build_h3_user_message(user_prompt, generation_mode, image_count=0,
                          no_bgm=False, extra_requirements="",
                          image_descriptions=None):
    """Build the H3 user message. generation_mode may be the full combo label
    ('H3 - 文生视频 (T2VA)') or the English core name. image_descriptions is the
    auto-caption list of reference images (index N -> <Picture N+1>)."""
    generation_mode = normalize_h3_mode(generation_mode)
    parts = [f"[Generation Mode] {generation_mode}"]

    if extra_requirements and extra_requirements.strip():
        parts.append(f"[Extra Requirements] {extra_requirements.strip()}")

    parts.append(f"[Mode Hint] {H3_MODE_HINTS.get(generation_mode, '')}")
    prompt_text = (user_prompt or "").strip()
    if prompt_text:
        parts.append(f"[User Original Prompt]\n{prompt_text}")
    else:
        parts.append("[User Original Prompt]\nNo text prompt was provided. Follow the selected mode and use any attached reference images as context.")

    if image_count > 0:
        parts.append(
            f"[Reference Images] {image_count} image(s) uploaded, labeled <Picture 1>..<Picture {image_count}> in order.\n"
            "Please write clear labels and usage for each image. "
            "Analyze subject appearance, scene style, composition, etc. from the images and incorporate into the prompt optimization.\n"
            + (build_reference_captions_block(image_descriptions) + "\n" if image_descriptions else "")
            + "If the user prompt refers to images by ordinal names such as \"图1/图2\", \"图片1\", or \"image 1\", "
            "map them in order to the standard labels <Picture 1>..<Picture N> and keep the mapping consistent."
        )
        if generation_mode == "Text to Video (T2VA)":
            parts.append(
                "[Note] Images detected. Please optimize using 'Image to Video' or 'Full Reference' mode."
            )

    if no_bgm:
        parts.append(
            "[Music] No background music is desired. Set non_diegetic_music to N/A."
        )
    else:
        parts.append(
            "[Music] Please suggest appropriate background music (non_diegetic_music) that matches the mood, style, and pacing of the video. Do NOT use N/A for non_diegetic_music unless absolutely no music fits the scene."
        )

    parts.append(
        "\nBased on the above information, optimize the prompt according to H3 specification. "
        "Output the optimized prompt directly without any explanation."
    )
    return "\n".join(parts)


def build_qwen_image_user_message(user_prompt, generation_mode, image_count=0,
                                  extra_requirements="", image_descriptions=None):
    """Build the Qwen-Image-2.1 user message. image_descriptions is the auto-caption
    list of reference images (index N -> <image N+1>)."""
    mode_hint = {
        "Qwen-Image-2.1 - 文生图": "Task: text-to-image. Build a complete image description from text.",
        "Qwen-Image-2.1 - 图像编辑": "Task: image editing. Apply only the requested changes and preserve every unrelated visual attribute.",
        "Qwen-Image-2.1 - 多参考图": "Task: multi-reference image composition/editing. State the role and retained attributes of each supplied reference image using <image1>, <image2>, etc.",
    }.get(generation_mode, "Task: image generation.")
    parts = [mode_hint]

    prompt_text = user_prompt or ""
    has_nine_grid = "九宫格" in prompt_text
    has_storyboard = "故事板" in prompt_text or "分镜头" in prompt_text
    is_t2i = generation_mode == "Qwen-Image-2.1 - 文生图"
    is_multi_reference = generation_mode == "Qwen-Image-2.1 - 多参考图"

    if has_nine_grid:
        if is_t2i:
            grid_rule = (
                "[九宫格规则：已由用户明确触发] 按用户要求创作严格的三行三列九个画格，"
                "明确从左到右、从上到下的阅读顺序，保持九格边界、间距和整体版式清楚。"
                "逐格呈现用户要求的内容；若用户表达连续事件，保持人物、服装、道具、空间和动作状态连续。"
                "仅凭'九宫格'不添加镜号、时间码、对白、标题或制作注释；只有同时触发故事板规则或用户明确要求时才添加。"
            )
        elif is_multi_reference:
            grid_rule = (
                "[九宫格规则：已由用户明确触发] 创作严格的三行三列九个画格，明确阅读顺序并保持版面清楚。"
                "先逐张绑定参考图标签与用途，再说明每格实际使用哪些参考图；保持身份、服装、产品及场景来源对应稳定。"
                "若用户表达连续事件，保持跨格状态连续。仅凭'九宫格'不添加镜号、时间码、对白、标题或制作注释；"
                "只有同时触发故事板规则或用户明确要求时才添加。参考图标签是提示词引用，不是画面文字。"
            )
        else:
            grid_rule = (
                "[九宫格规则：已由用户明确触发] 若输入图本身是九宫格，按用户指定的画格或区域执行编辑，"
                "保持未指定画格、格线、间距、阅读顺序和整体布局不变；若用户要求重做整张版面，再按要求调整。"
                "若输入图不是九宫格而用户要求将其编排成九宫格，明确新布局及原图内容的保留方式。"
                "仅凭'九宫格'不添加镜号、时间码、对白、标题或制作注释；只有同时触发故事板规则或用户明确要求时才添加。"
            )
        parts.append(grid_rule)

    if has_storyboard:
        storyboard_rule = (
            "[故事板/分镜头规则：已由用户明确触发] 按制作型故事板组织画面；尊重用户指定的格数，"
            "未指定时根据剧情拍点决定，不因触发词自动强制九格。每格表现一个主要时刻，明确镜号或顺序、"
            "景别/视角、主体位置与动作，并保持人物、服装、道具、空间方向、光线和状态连续。"
            "默认在画格外设置清楚的注释区域；镜号、时间（仅在有时长依据时）、镜头说明、用户提供的对白/字幕、声音和转场"
            "均作为板面注释，不覆盖剧情画面。若用户明确要求纯视觉、无文字、无编号、不要说明或关键帧板，则省略注释与文字。"
            "逐字保留用户给定文字，不编造对白、品牌或剧情事实；无对白时不虚构台词。"
        )
        if is_multi_reference:
            storyboard_rule += (
                "先逐张说明每个 <imageN> 的身份、服装、产品、场景、姿态、风格或画布用途；"
                "再在每格标明实际使用的参考图标签，未出现在该格的素材不强行加入。"
            )
        elif not is_t2i:
            storyboard_rule += (
                "若编辑现有故事板，只修改用户指定的格子或板面元素，并保持其余画格及其注释对应关系不变。"
            )
        parts.append(storyboard_rule)

    if extra_requirements and extra_requirements.strip():
        parts.append(f"[Extra Requirements] {extra_requirements.strip()}")
    prompt_text = (user_prompt or "").strip()
    if prompt_text:
        parts.append(f"[User Original Prompt]\n{prompt_text}")
    else:
        parts.append("[User Original Prompt]\nNo text prompt was provided. Follow the selected prompt rules and use any attached reference images as context.")

    if image_count > 0:
        refs = ", ".join(f"<image{i + 1}>" for i in range(image_count))
        parts.append(
            f"[Reference Images] {image_count} image(s) uploaded: {refs}. "
            "Analyze their visible details before writing the optimized prompt.\n"
            + (build_reference_captions_block(image_descriptions) + "\n" if image_descriptions else "")
            + "If the user prompt refers to images by ordinal names such as \"图1/图2\", \"图片1\", or \"image 1\", "
            "map them in order to the standard tags <image1>, <image2>, ... and use ONLY these standard tags in the output."
        )
    parts.append("Output the optimized prompt directly without any explanation.")
    return "\n".join(parts)


def build_messages(system_prompt, user_message, image_uris=None, image_label="<Picture {n}>"):
    """Build LLM messages, optionally multimodal.

    image_label is a template with a '{n}' placeholder, e.g. '<Picture {n}>' or '<image{n}>'.
    """
    if image_uris:
        user_content = [{"type": "text", "text": user_message}]
        for idx, uri in enumerate(image_uris):
            label = image_label.format(n=idx + 1)
            user_content.append({"type": "image_url", "image_url": {"url": uri}})
            user_content.append({"type": "text", "text": f"(Above is {label})"})
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def split_bilingual_output(text):
    """Split an H3 bilingual reply into (english, chinese)."""
    text = text or ""
    cn_marker = re.search(r"(?is)<XZG_CHINESE_PROMPT>\s*", text)
    en_marker = re.search(r"(?is)<XZG_ENGLISH_PROMPT>\s*", text)
    if not cn_marker:
        cn_marker = re.search(
            r"(?im)^\s*[#>*`\-]*\s*(?:中文(?:版本|提示词)?|chinese\s+(?:version|prompt))\s*[:：\-]*\s*$",
            text,
        )
    if not en_marker:
        en_marker = re.search(
            r"(?im)^\s*[#>*`\-]*\s*(?:英文(?:版本|提示词)?|english\s+(?:version|prompt))\s*[:：\-]*\s*$",
            text,
        )
    if not cn_marker or not en_marker:
        # Model did not follow the format; keep the result to avoid silent loss.
        return text.strip(), ""

    if cn_marker.start() < en_marker.start():
        chinese = text[cn_marker.end():en_marker.start()].strip()
        english = text[en_marker.end():].strip()
    else:
        english = text[en_marker.end():cn_marker.start()].strip()
        chinese = text[cn_marker.end():].strip()
    return english, chinese
