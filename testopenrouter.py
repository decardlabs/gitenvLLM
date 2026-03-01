import os
import requests

API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv("OPENROUTER_API_KEY")

def main() -> None:
	if not API_KEY:
		raise ValueError("Missing OPENROUTER_API_KEY environment variable.")
	headers = {
		"Authorization": f"Bearer {API_KEY}",
		"HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://example.com"),
		"X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "Local Python Script"),
	}

	payload = {
		"model": "openai/gpt-5.2",
		"messages": [
			{
				"role": "user",
				"content": "What is the meaning of life?",
			}
		],
	}
	try:
		response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
		response.raise_for_status()
	except requests.exceptions.RequestException as exc:
		raise SystemExit(f"Request failed: {exc}") from exc

	try:
		result = response.json()
	except ValueError as exc:
		raise SystemExit(f"Invalid JSON response: {response.text}") from exc

	choice = result.get("choices", [{}])[0]
	message = choice.get("message", {})
	content = message.get("content")

	if content:
		print(content)
	else:
		print(result)


if __name__ == "__main__":
	main()
