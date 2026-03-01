import os
import json
import time
import argparse
import requests
from dotenv import load_dotenv
from datetime import datetime

GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# ====================== 1. 测试用例库（6大维度，全面测试编程能力）======================
TEST_CASES = [
    {
        "id": 1,
        "category": "基础算法",
        "title": "快速排序实现",
        "prompt": "用 Python 实现一个稳定的快速排序算法，要求处理重复元素，包含注释和测试用例",
        "check_points": ["实现快速排序", "处理重复元素", "代码可运行", "包含测试用例"]
    },
    {
        "id": 2,
        "category": "数据结构",
        "title": "二叉树层序遍历",
        "prompt": "用 Python 实现二叉树的层序遍历（BFS），定义树节点结构，提供测试代码",
        "check_points": ["树节点定义", "BFS 实现", "代码可运行", "输出正确"]
    },
    {
        "id": 3,
        "category": "代码调试",
        "title": "修复bug代码",
        "prompt": "下面代码有bug，修复并解释原因：\ndef calc(a,b): return a/b\nprint(calc(10,0))",
        "check_points": ["捕获除零异常", "代码可运行", "给出解释"]
    },
    {
        "id": 4,
        "category": "工程开发",
        "title": "日志工具类",
        "prompt": "用 Python 写一个通用日志工具类，支持文件输出+控制台输出，可设置日志级别",
        "check_points": ["类封装", "文件+控制台", "日志级别", "可直接使用"]
    },
    {
        "id": 5,
        "category": "并发编程",
        "title": "多线程下载器",
        "prompt": "用 Python threading 实现简单多线程文件下载器，支持传入URL列表",
        "check_points": ["多线程实现", "下载功能", "异常处理"]
    },
    {
        "id": 6,
        "category": "设计模式",
        "title": "单例模式实现",
        "prompt": "用 Python 实现线程安全的单例模式，提供使用示例",
        "check_points": ["单例正确", "线程安全", "使用示例"]
    },
    {
        "id": 7,
        "category": "SQL 编程",
        "title": "SQL 查询编写",
        "prompt": "有 user(id,name,age,create_time) 表，查询近30天注册、年龄18-30的用户，按时间倒序",
        "check_points": ["SQL 语法正确", "条件正确", "排序正确"]
    },
    {
        "id": 8,
        "category": "实战编程",
        "title": "CSV 数据处理",
        "prompt": "用 Python 读取 csv 文件，计算某一列平均值，处理空值和异常",
        "check_points": ["csv 处理", "空值处理", "异常捕获", "计算正确"]
    }
]

CHECK_POINT_KEYWORDS = {
    "实现快速排序": ["快速排序", "quick sort", "quicksort"],
    "处理重复元素": ["重复", "重复元素", "duplicate"],
    "代码可运行": ["def ", "if __name__", "示例", "example", "测试"],
    "包含测试用例": ["测试", "assert", "unittest", "pytest", "示例"],
    "树节点定义": ["TreeNode", "class", "节点"],
    "BFS 实现": ["bfs", "队列", "deque", "层序"],
    "输出正确": ["输出", "print", "result", "返回"],
    "捕获除零异常": ["zerodivision", "try", "except", "除零"],
    "给出解释": ["原因", "解释", "because", "说明"],
    "类封装": ["class", "__init__", "实例"],
    "文件+控制台": ["filehandler", "streamhandler", "文件", "控制台"],
    "日志级别": ["debug", "info", "warning", "error", "日志级别"],
    "可直接使用": ["示例", "main", "调用", "usage"],
    "多线程实现": ["threading", "thread", "线程"],
    "下载功能": ["download", "请求", "保存", "urlopen", "requests.get"],
    "异常处理": ["try", "except", "异常", "error"],
    "单例正确": ["singleton", "单例"],
    "线程安全": ["lock", "线程安全", "互斥"],
    "使用示例": ["示例", "example", "调用"],
    "SQL 语法正确": ["select", "from", "where"],
    "条件正确": ["30", "18", "30", "between", "date_sub", "create_time"],
    "排序正确": ["order by", "desc", "倒序"],
    "csv 处理": ["csv", "read", "reader", "pandas"],
    "空值处理": ["空值", "none", "nan", "strip", "if"],
    "异常捕获": ["try", "except", "异常", "error"],
    "计算正确": ["平均", "mean", "sum", "count", "avg"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GLM 编程能力自动化测试")
    parser.add_argument("--model", default=os.getenv("GLM_MODEL", "glm-4"), help="测试模型名")
    parser.add_argument("--temperature", type=float, default=float(os.getenv("GLM_TEMPERATURE", "0.3")), help="采样温度")
    parser.add_argument("--timeout", type=float, default=float(os.getenv("GLM_TIMEOUT", "60")), help="请求超时秒数")
    parser.add_argument("--sleep", type=float, default=float(os.getenv("GLM_SLEEP_SECONDS", "1")), help="每个用例间隔秒数")
    parser.add_argument("--output", default=None, help="自定义报告输出文件名")
    parser.add_argument("--api-url", default=os.getenv("GLM_API_URL", GLM_API_URL), help="GLM chat completions 接口地址")
    return parser.parse_args()


# ====================== 2. GLM API 调用工具 ======================
def call_glm(prompt: str, model: str, api_key: str, api_url: str, temperature: float, timeout: float) -> dict:
    """调用 GLM 大模型接口，返回结构化结果"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        choices = result.get("choices") or []
        if not choices:
            return {"ok": False, "answer": "", "error": "响应中不存在 choices 字段"}
        message = choices[0].get("message") if isinstance(choices[0], dict) else {}
        content = message.get("content") if isinstance(message, dict) else None
        if not content:
            return {"ok": False, "answer": "", "error": "响应中不存在 message.content 字段"}
        return {"ok": True, "answer": str(content), "error": ""}
    except Exception as e:
        return {"ok": False, "answer": "", "error": f"API 调用失败：{str(e)}"}


def point_passed(answer: str, point: str) -> bool:
    keywords = CHECK_POINT_KEYWORDS.get(point)
    if not keywords:
        keywords = [point]
    answer_lower = answer.lower()
    return any(keyword.lower() in answer_lower for keyword in keywords)

# ====================== 3. 自动评分引擎 ======================
def auto_check_answer(answer: str, check_points: list) -> dict:
    """自动检查答案并评分"""
    passed = 0
    total = len(check_points)
    result = {}

    # 关键词规则评分（可升级为 AST/执行级验证）
    for point in check_points:
        if point_passed(answer, point):
            passed += 1
            result[point] = "✅ 通过"
        else:
            result[point] = "❌ 未通过"

    score = round(passed / total * 100, 2)
    return {
        "detail": result,
        "passed_num": passed,
        "total_num": total,
        "score": score
    }


def build_failed_result(check_points: list, error: str) -> dict:
    detail = {point: "❌ 未通过（API失败）" for point in check_points}
    return {
        "detail": detail,
        "passed_num": 0,
        "total_num": len(check_points),
        "score": 0,
        "error": error,
    }

# ====================== 4. 执行测试 & 生成报告 ======================
def run_glm_test(model: str, api_key: str, api_url: str, temperature: float, timeout: float, sleep_seconds: float) -> dict:
    """执行全部测试用例"""
    test_results = []
    total_score = 0
    start_time = time.time()

    print(f"🚀 开始测试 GLM 编程能力（模型：{model}）")
    print(f"🌐 接口地址：{api_url}")
    print("=" * 80)

    for case in TEST_CASES:
        print(f"\n📌 执行测试用例 {case['id']}：{case['title']}")
        call_result = call_glm(
            prompt=case["prompt"],
            model=model,
            api_key=api_key,
            api_url=api_url,
            temperature=temperature,
            timeout=timeout,
        )

        if call_result["ok"]:
            answer = call_result["answer"]
            check_result = auto_check_answer(answer, case["check_points"])
            status_text = "✅"
        else:
            answer = call_result["error"]
            check_result = build_failed_result(case["check_points"], call_result["error"])
            status_text = "❌"

        # 保存结果
        case_result = {
            **case,
            "model_answer": answer,
            "api_ok": call_result["ok"],
            "api_error": call_result["error"],
            "check_result": check_result,
        }
        test_results.append(case_result)
        total_score += check_result["score"]
        print(f"{status_text} 得分：{check_result['score']} 分 | {check_result['passed_num']}/{check_result['total_num']} 检查点通过")
        if not call_result["ok"]:
            print(f"   错误：{call_result['error']}")
        time.sleep(max(0, sleep_seconds))

    # 统计
    cost_time = round(time.time() - start_time, 2)
    avg_score = round(total_score / len(TEST_CASES), 2)
    pass_rate = round(len([r for r in test_results if r["check_result"]["score"] >= 60]) / len(test_results) * 100, 2)

    return {
        "model": model,
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cost_time": cost_time,
        "total_cases": len(TEST_CASES),
        "avg_score": avg_score,
        "pass_rate": pass_rate,
        "details": test_results
    }

# ====================== 5. 导出测试报告 ======================
def generate_report(report_data: dict, output_file: str | None = None):
    """生成格式化测试报告（控制台 + 文件）"""
    model = report_data["model"]
    filename = output_file or f"GLM编程能力测试报告_{model}_{datetime.now().strftime('%Y%m%d%H%M')}.md"

    # 控制台输出
    print("\n" + "=" * 80)
    print("📄 GLM 编程能力综合测试报告")
    print("=" * 80)
    print(f"🧩 测试模型：{report_data['model']}")
    print(f"🕒 测试时间：{report_data['test_time']}")
    print(f"⌛ 耗时：{report_data['cost_time']} 秒")
    print(f"📊 总用例数：{report_data['total_cases']} 个")
    print(f"🎯 平均得分：{report_data['avg_score']} 分")
    print(f"✅ 测试通过率：{report_data['pass_rate']}%")
    print("=" * 80)

    # Markdown 报告内容
    md_content = f"""# GLM 编程能力综合测试报告
**测试模型**：{report_data['model']}
**测试时间**：{report_data['test_time']}
**总耗时**：{report_data['cost_time']} 秒
**总用例数**：{report_data['total_cases']} 个
**平均得分**：{report_data['avg_score']} 分
**测试通过率**：{report_data['pass_rate']}%

## 测试详情
"""
    for case in report_data["details"]:
        md_content += f"""
### {case['id']}. {case['title']}
- 分类：{case['category']}
- API 调用：{'成功' if case.get('api_ok') else '失败'}
- 得分：{case['check_result']['score']} 分
- 检查点：
"""
        for k, v in case["check_result"]["detail"].items():
            md_content += f"  - {k}：{v}\n"
        if case.get("api_error"):
            md_content += f"- API 错误：{case['api_error']}\n"
        md_content += f"\n**模型输出**：\n```\n{case['model_answer']}\n```\n---\n"

    # 保存文件
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n📄 测试报告已保存：{filename}")
    return filename

# ====================== 主入口 ======================
if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    api_key = os.getenv("GLM_API_KEY")

    if not api_key:
        print("❌ 请在 .env 文件中配置 GLM_API_KEY")
    else:
        report = run_glm_test(
            model=args.model,
            api_key=api_key,
            api_url=args.api_url,
            temperature=args.temperature,
            timeout=args.timeout,
            sleep_seconds=args.sleep,
        )
        generate_report(report, output_file=args.output)