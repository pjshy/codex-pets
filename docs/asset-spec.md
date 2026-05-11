# 素材接入说明

本项目面向 **Codex custom pet** 打包，不面向独立桌面 app。

## 目标格式

最终要交付给 Codex 的是：

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
├── pet.json
└── spritesheet.webp
```

其中 `spritesheet.webp` 需要满足固定 atlas 约束：

- 尺寸：`1536x1872`
- 网格：`8 x 9`
- 单格：`192x208`
- 背景：透明
- 未使用格子：全透明

## 最小素材集

如果你要替换当前 pet，建议至少提供：

- 角色主视图：透明背景 `png` 或 `webp`
- 建议先覆盖 3 个核心状态：
  - `idle`
  - `interactive`
  - `focus`

如果后续要扩展成更完整的 Codex pet，再继续补：

- `running-right`
- `running-left`
- `waving`
- `jumping`
- `failed`
- `waiting`
- `running`
- `review`

## 推荐素材形态

- 每个状态 4 到 8 帧逐帧动画
- 单独尾巴 / 耳朵 / 表情图层，便于后续微调
- 长边建议 `512px` 或 `1024px`
- 素材本身尽量已经抠成透明底

## 命名建议

```text
assets/
  pet/
    idle-01.png
    idle-02.png
    interactive-01.png
    focus-01.png
    review-01.png
```

## 我们会如何使用这些素材

- 把帧贴到固定 `8 x 9` 的 atlas 上
- 输出 Codex 可读取的 `spritesheet.webp`
- 生成对应的 `pet.json`
- 安装到 `~/.codex/pets/<pet-id>/`
