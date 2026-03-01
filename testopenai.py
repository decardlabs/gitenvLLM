import os
import sys

from openai import OpenAI


def main() -> int:
  api_key = os.getenv("OPENROUTER_API_KEY")
  if not api_key:
    print("Missing OPENROUTER_API_KEY environment variable.")
    return 1

  model = (
    os.getenv("OPENROUTER_MODEL")
    or os.getenv("LLM_MODEL")
    or os.getenv("OPENAI_MODEL")
  )
  if not model:
    print("Missing model env var. Set OPENROUTER_MODEL or LLM_MODEL or OPENAI_MODEL.")
    return 1

  client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=api_key,
  )

  try:
    completion = client.chat.completions.create(
      extra_headers={
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://example.com"),
        "X-OpenRouter-Title": os.getenv("OPENROUTER_SITE_NAME", "Local OpenAI SDK Script"),
      },
      model=model,
      messages=[
        {
          "role": "user",
          "content": "What is the meaning of life?",
        }
      ],
    )
  except Exception as exc:  # noqa: BLE001
    print(f"Request failed: {exc}")
    return 1

  choices = getattr(completion, "choices", None) or []
  if not choices:
    print("No choices returned from API.")
    print(completion)
    return 1

  content = choices[0].message.content
  if content:
    print(content)
  else:
    print("Empty message content returned.")
    print(completion)

  return 0


if __name__ == "__main__":
  sys.exit(main())
