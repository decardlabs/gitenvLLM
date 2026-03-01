# 大模型测试脚本集合

本仓库用于测试不同模型与网关的接口可用性、基础编程输出质量与批量评测能力。

## 当前维护脚本

- `run.py`：统一运行入口（推荐）
- `test.py`：通用 OpenAI 兼容接口连通性测试（支持批量模型）
- `testopenrouter.py`：OpenRouter + requests 最小请求示例
- `testopenai.py`：OpenRouter + OpenAI SDK 示例
- `testGLM.py`：GLM 编程能力批量评测与报告导出
- `testDeepSeek.py`：DeepSeek 编程能力批量评测与报告导出

## 快速开始

### 1) 创建并激活虚拟环境（macOS/Linux）

```bash
python -m venv venv
source venv/bin/activate
```

### 2) 安装依赖

```bash
pip install -r requirements.txt
```

### 3) 配置环境变量

```bash
cp .env.example .env
```

把 `.env` 中的占位符替换为真实 API Key 与模型名。

## 统一入口运行（推荐）

```bash
python3 run.py test --base-url "https://openrouter.ai/api" --model "openai/gpt-5.2"
python3 run.py openrouter
python3 run.py openai
python3 run.py glm --model glm-4 --output glm_report.md
python3 run.py deepseek --model deepseek-chat --output deepseek_report.md
```

## 原始脚本运行

```bash
python3 test.py --base-url "https://openrouter.ai/api" --model "openai/gpt-5.2"
python3 testopenrouter.py
python3 testopenai.py
python3 testGLM.py --model glm-4 --output glm_report.md
python3 testDeepSeek.py --model deepseek-chat --output deepseek_report.md
```

## 关键环境变量

### 通用/兼容接口（`test.py`）

- `LLM_BASE_URL` / `OPENAI_BASE_URL`
- `LLM_API_KEY` / `OPENAI_API_KEY`
- `LLM_MODEL` / `OPENAI_MODEL`
- `LLM_MODELS` / `OPENAI_MODELS`（可选，逗号分隔）

### OpenRouter（`testopenrouter.py` / `testopenai.py`）

- 必填：`OPENROUTER_API_KEY`
- 常用：`OPENROUTER_MODEL`
- 可选：`OPENROUTER_BASE_URL`、`OPENROUTER_SITE_URL`、`OPENROUTER_SITE_NAME`

### GLM 评测（`testGLM.py`）

- 必填：`GLM_API_KEY`
- 可选：`GLM_MODEL`、`GLM_API_URL`、`GLM_TEMPERATURE`、`GLM_TIMEOUT`、`GLM_SLEEP_SECONDS`

### DeepSeek 评测（`testDeepSeek.py`）

- 必填：`DEEPSEEK_API_KEY`
- 可选：`DEEPSEEK_MODEL`、`DEEPSEEK_API_URL`、`DEEPSEEK_TEMPERATURE`、`DEEPSEEK_TIMEOUT`、`DEEPSEEK_SLEEP_SECONDS`

## 脚本选型建议

- 只做接口连通性与批量模型巡检：`test.py`
- 看最底层 HTTP 请求细节：`testopenrouter.py`
- 用 SDK 方式接入 OpenRouter：`testopenai.py`
- 要做 GLM 编程能力打分与报告：`testGLM.py`
- 要做 DeepSeek 编程能力打分与报告：`testDeepSeek.py`

## 可运行性检查（已完成）

本仓库已完成以下检查：

- 全部 Python 脚本语法编译通过（`compileall`）
- CLI 参数入口正常（`run.py -h`、`test.py -h`、`testGLM.py -h`、`testDeepSeek.py -h`）

说明：真实 API 调用依赖有效密钥与网络环境，未在文档检查阶段强制执行在线请求。

## 常用 Git 指令

```bash
git status
git add .
git commit -m "chore: finalize scripts and docs"
git pull --rebase origin main
git push
```
