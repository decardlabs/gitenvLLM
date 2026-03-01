# 大模型测试脚本集合

这个仓库是一组用于测试大模型接口可用性的 Python 脚本，覆盖了不同调用方式：标准库 HTTP、`requests`、OpenAI SDK（走 OpenRouter 网关）。

## 脚本清单与特点

### `test.py`

定位：通用连通性与批量模型测试脚本（推荐优先使用）。

特点：
- 仅依赖 Python 标准库（无第三方包）。
- 支持命令行参数和环境变量两种配置方式。
- 支持单模型与多模型批量测试（`--models`）。
- 自动尝试两种路径：`/v1/chat/completions` 和 `/chat/completions`，兼容性更好。
- 输出成功/失败、耗时、错误原因，并返回合适退出码（0/1）。

适合场景：CI 连通性检查、网关迁移验证、模型白名单批量巡检。

---

### `testopenrouter.py`

定位：使用 `requests` 直接调用 OpenRouter Chat Completions 的简洁脚本。

特点：
- 基于 HTTP 原始请求，便于理解请求头和请求体细节。
- 使用 `OPENROUTER_API_KEY` 等环境变量，避免硬编码密钥。
- 内置超时与异常处理，失败时能快速定位问题。
- 结构清晰，适合作为“最小可运行示例”和排障模板。

适合场景：快速验证 OpenRouter 单模型调用、学习接口字段含义、调试请求参数。

---

### `testopenai.py`

定位：使用 OpenAI Python SDK 调用 OpenRouter（通过 `base_url`）的示例脚本。

特点：
- 使用 SDK 调用，代码量少、可读性高。
- 通过 `OPENROUTER_BASE_URL`、`OPENROUTER_MODEL` 等环境变量可灵活切换。
- 包含基础异常处理和返回内容兜底，适合日常本地验证。
- 与原生 OpenAI SDK 习惯一致，后续迁移成本低。

适合场景：你项目里本来就使用 OpenAI SDK，希望最小改动接入 OpenRouter。

## 开发环境与测试流程

以下命令用于本项目开发过程中的虚拟环境管理、依赖安装与测试准备。

### 1) 创建并激活虚拟环境（macOS/Linux）

```bash
python -m venv venv
source venv/bin/activate
```

### 2) 安装依赖

```bash
pip install requests openai
```

### 3) 检查当前环境已安装包

```bash
pip list
```

### 4) 运行测试脚本

```bash
python3 test.py --base-url "https://openrouter.ai/api" --model "openai/gpt-5.2"
python3 testopenrouter.py
python3 testopenai.py
```

### 5) 导出与复用依赖

```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

### 6) 退出虚拟环境

```bash
deactivate
```

## 开发过程常用 Git 指令

以下指令覆盖日常开发中最常用的 Git 操作，便于快速上手和排查。

### 1) 首次初始化与远程仓库

```bash
git init
git remote add origin <your-repo-url>
git remote -v
```

### 2) 查看状态与差异

```bash
git status
git diff
git diff --staged
```

### 3) 新建与切换分支

```bash
git branch
git checkout -b feature/your-feature
git switch main
```

### 4) 提交代码

```bash
git add .
git commit -m "feat: add model test script"
git log --oneline --graph -n 10
```

### 5) 同步远程仓库

```bash
git pull --rebase origin main
git push -u origin feature/your-feature
```

### 6) 合并与删除分支

```bash
git checkout main
git merge feature/your-feature
git branch -d feature/your-feature
```

### 7) 撤销与回退（谨慎使用）

```bash
git restore <file>
git restore --staged <file>
git reset --soft HEAD~1
git reset --hard HEAD~1
```

### 8) 临时保存现场

```bash
git stash
git stash list
git stash pop
```

### 9) 推荐开发节奏

```bash
git checkout -b feature/xxx
git add .
git commit -m "feat: ..."
git pull --rebase origin main
git push -u origin feature/xxx
```

## 快速使用

### 1) 准备环境变量（macOS/Linux）

```bash
export OPENROUTER_API_KEY="你的key"
export OPENROUTER_MODEL="openai/gpt-5.2"
export OPENROUTER_SITE_URL="https://example.com"
export OPENROUTER_SITE_NAME="LLM Test"
```

说明：
- `testopenai.py` 会从 `OPENROUTER_MODEL` / `LLM_MODEL` / `OPENAI_MODEL` 读取模型名（至少设置一个）。
- `test.py` 优先使用命令行参数，其次读取 `LLM_MODEL` / `OPENAI_MODEL`。

### 2) 运行脚本

```bash
python3 test.py --base-url "https://openrouter.ai/api" --model "openai/gpt-5.2"
python3 testopenrouter.py
python3 testopenai.py
```

## 依赖说明

- `test.py`：无第三方依赖。
- `testopenrouter.py`：需要 `requests`。
- `testopenai.py`：需要 `openai`。

可安装：

```bash
pip install requests openai
```

## 选型建议

- 要“最稳健批量验证”：用 `test.py`。
- 要“看清 HTTP 细节”：用 `testopenrouter.py`。
- 要“贴近应用代码（SDK）”：用 `testopenai.py`。
