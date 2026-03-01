from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def normalize_base_url(base_url: str) -> str:
	return base_url.rstrip("/")


def build_candidate_urls(base_url: str) -> list[str]:
	normalized = normalize_base_url(base_url)

	if normalized.endswith("/v1"):
		return [f"{normalized}/chat/completions"]

	return [
		f"{normalized}/v1/chat/completions",
		f"{normalized}/chat/completions",
	]


def send_chat_request(
	url: str,
	api_key: str,
	model: str,
	timeout: float,
	prompt: str,
	max_tokens: int,
) -> tuple[int, dict, float]:
	payload = {
		"model": model,
		"messages": [{"role": "user", "content": prompt}],
		"temperature": 0,
		"max_tokens": max_tokens,
	}
	data = json.dumps(payload).encode("utf-8")

	request = urllib.request.Request(
		url=url,
		data=data,
		method="POST",
		headers={
			"Authorization": f"Bearer {api_key}",
			"Content-Type": "application/json",
		},
	)

	start = time.perf_counter()
	with urllib.request.urlopen(request, timeout=timeout) as response:
		elapsed = time.perf_counter() - start
		response_text = response.read().decode("utf-8", errors="replace")
		response_json = json.loads(response_text)
		return response.status, response_json, elapsed


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="测试大模型是否可用（OpenAI 兼容 Chat Completions 接口）"
	)
	parser.add_argument(
		"--base-url",
		default=os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL"),
		help="接口基础地址，例如 https://api.openai.com（也可用环境变量 LLM_BASE_URL 或 OPENAI_BASE_URL）",
	)
	parser.add_argument(
		"--api-key",
		default=os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY"),
		help="API Key（也可用环境变量 LLM_API_KEY 或 OPENAI_API_KEY）",
	)
	parser.add_argument(
		"--model",
		default=os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL"),
		help="模型名，例如 gpt-4o-mini（也可用环境变量 LLM_MODEL 或 OPENAI_MODEL）",
	)
	parser.add_argument(
		"--models",
		default=os.getenv("LLM_MODELS") or os.getenv("OPENAI_MODELS"),
		help="批量模型名（逗号分隔），例如 gpt-4o-mini,gpt-4.1",
	)
	parser.add_argument("--timeout", type=float, default=30.0, help="请求超时秒数，默认 30")
	parser.add_argument(
		"--prompt",
		default=os.getenv("LLM_PROMPT") or os.getenv("OPENAI_PROMPT") or "请回复：连接测试成功",
		help="测试提示词（也可用环境变量 LLM_PROMPT 或 OPENAI_PROMPT）",
	)
	parser.add_argument("--max-tokens", type=int, default=32, help="最大生成 token，默认 32")
	args = parser.parse_args()

	if args.models:
		parsed_models = [item.strip() for item in args.models.split(",") if item.strip()]
		args.models = parsed_models
		if not args.model and parsed_models:
			args.model = parsed_models[0]
	else:
		args.models = []

	missing = []
	if not args.base_url:
		missing.append("base_url（--base-url 或环境变量 LLM_BASE_URL/OPENAI_BASE_URL）")
	if not args.api_key:
		missing.append("api_key（--api-key 或环境变量 LLM_API_KEY/OPENAI_API_KEY）")
	if not args.model and not args.models:
		missing.append("model（--model 或环境变量 LLM_MODEL/OPENAI_MODEL）")

	if missing:
		parser.error("缺少必要参数：" + "；".join(missing))

	return args


def extract_content(body: dict | object) -> str | None:
	content = None
	choices = body.get("choices") if isinstance(body, dict) else None
	if isinstance(choices, list) and choices:
		message = choices[0].get("message") if isinstance(choices[0], dict) else None
		if isinstance(message, dict):
			content = message.get("content")
	return content


def test_one_model(args: argparse.Namespace, model: str, candidate_urls: list[str]) -> tuple[bool, str]:
	last_error = None
	for url in candidate_urls:
		try:
			status, body, elapsed = send_chat_request(
				url=url,
				api_key=args.api_key,
				model=model,
				timeout=args.timeout,
				prompt=args.prompt,
				max_tokens=args.max_tokens,
			)

			content = extract_content(body)

			print("✅ 模型连接测试成功")
			print(f"- 模型: {model}")
			print(f"- URL: {url}")
			print(f"- HTTP Status: {status}")
			print(f"- 耗时: {elapsed:.2f}s")
			if content:
				print(f"- 返回内容: {content}")
			else:
				print("- 返回内容: （未解析到 message.content，原始响应如下）")
				print(json.dumps(body, ensure_ascii=False, indent=2))
			return True, ""

		except urllib.error.HTTPError as error:
			error_body = error.read().decode("utf-8", errors="replace")
			last_error = (
				f"HTTPError | model={model} | URL={url} | status={error.code} | body={error_body}"
			)
		except urllib.error.URLError as error:
			last_error = f"URLError | model={model} | URL={url} | reason={error.reason}"
		except TimeoutError:
			last_error = f"TimeoutError | model={model} | URL={url} | timeout={args.timeout}s"
		except json.JSONDecodeError as error:
			last_error = f"JSONDecodeError | model={model} | URL={url} | detail={error}"
		except Exception as error:  # noqa: BLE001
			last_error = f"UnexpectedError | model={model} | URL={url} | detail={error}"

	print("❌ 模型连接测试失败")
	print(f"- 模型: {model}")
	if last_error:
		print(f"- 错误详情: {last_error}")
	return False, last_error or "未知错误"


def main() -> int:
	args = parse_args()
	candidate_urls = build_candidate_urls(args.base_url)
	target_models = args.models if args.models else [args.model]

	if len(target_models) == 1:
		success, _ = test_one_model(args, target_models[0], candidate_urls)
		return 0 if success else 1

	print("📌 批量模型测试开始")
	print(f"- 总模型数: {len(target_models)}")
	print()

	results = []
	for index, model in enumerate(target_models, start=1):
		print(f"===== [{index}/{len(target_models)}] 测试模型: {model} =====")
		success, detail = test_one_model(args, model, candidate_urls)
		results.append((model, success, detail))
		print()

	success_count = sum(1 for _, success, _ in results if success)
	fail_count = len(results) - success_count

	print("📊 批量测试汇总")
	print(f"- 成功: {success_count}")
	print(f"- 失败: {fail_count}")

	for model, success, detail in results:
		status = "PASS" if success else "FAIL"
		print(f"- [{status}] {model}")
		if not success and detail:
			print(f"  错误: {detail}")

	return 0 if fail_count == 0 else 1


if __name__ == "__main__":
	sys.exit(main())
