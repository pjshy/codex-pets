# codex-pets

`codex-pets` 是一个 **Codex custom pet 打包项目**。

- `pet.json`
- `spritesheet.webp`

## 这是什么

这个仓库主要负责三件事：

- 管理 pet 源素材
- 维护 Codex pet atlas 约束
- 生成并安装可供 Codex 使用的 custom pet 包

## 一条命令

仓库只保留一个统一命令入口：

```bash
npm run pet -- <action>
```

支持的 action：

```bash
npm run pet -- build
npm run pet -- install
npm run pet -- reinstall
```

含义：

- `build`: 只生成打包产物
- `install`: 只安装现有打包产物
- `reinstall`: 重新生成并覆盖安装

## 快速开始

1. 生成并安装当前 pet：

```bash
npm run pet -- reinstall
```

2. 重启 Codex，或在 Codex 设置里刷新 custom pets。

## 产物格式

生成结果位于：

```text
dist/codex-pets-package/codex-pets/
```

最终用于 Codex 的最小包结构是：

```text
${CODEX_HOME:-$HOME/.codex}/pets/<pet-id>/
├── pet.json
└── spritesheet.webp
```

其中 `spritesheet.webp` 需要满足固定 contract：

- `1536x1872`
- `8 x 9` 网格
- 单格 `192x208`
- 透明背景
- 未使用格子全透明

## 仓库结构

```text
assets/   # pet 源素材
docs/     # 约束与说明
scripts/  # 打包与安装脚本
```

关键文件：

- `docs/asset-spec.md`: 素材和 atlas 约束
- `scripts/pet_package.py`: build/install/reinstall 核心逻辑
- `scripts/pet.mjs`: npm 入口，自动选择可用的 Python 运行时

## 素材说明

当前脚本假定 `assets/` 下存在可用于组装 atlas 的透明 PNG 素材。动画效果目前以“固定素材 + framing/scale/rotation 变化”的方式合成，适合快速验证 custom pet 效果，但不替代正式的逐帧动画制作。

如果你要提升动画质量，下一步应该优先升级 `assets/` 中的源图，而不是修改 `pet.json`。
