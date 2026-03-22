import argparse
import asyncio
import json
import urllib.parse
from pathlib import Path

# 用法示例：
# 1) 仅检测 401：
#    python cpa_utils.py --cpa-token Bearer_xxx
# 2) 指定 CPA 地址并删除 401：
#    python cpa_utils.py --cpa-base-url http://localhost:8317 --cpa-token Bearer_xxx --delete
# 3) 保存检测结果到 JSON 文件：
#    python cpa_utils.py --cpa-token Bearer_xxx --output result.json
# 4) 批量上传目录下 JSON：
#    python cpa_utils.py --cpa-token Bearer_xxx --upload-dir ./tokens

try:
    import aiohttp
except ImportError:
    aiohttp = None

import requests

DEFAULT_MGMT_UA = "codex_cli_rs/0.76.0 (Debian 13.0.0; x86_64) WindowsTerminal"


def _mgmt_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _safe_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return {}


def _extract_account_id(item: dict):
    for key in ("chatgpt_account_id", "chatgptAccountId", "account_id", "accountId"):
        val = item.get(key)
        if val:
            return str(val)
    return None


def _get_item_type(item: dict) -> str:
    return str(item.get("type") or item.get("typo") or "")


def _read_json_file(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _upload_one_json(base_url: str, token: str, path: Path, timeout: int = 30) -> bool:
    if not path.exists() or not path.is_file():
        return False
    data = _read_json_file(path)
    if data is None:
        return False
    content = json.dumps(data, ensure_ascii=False).encode("utf-8")
    files = {"file": (path.name, content, "application/json")}
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(f"{base_url}/v0/management/auth-files", files=files, headers=headers, timeout=timeout)
        return resp.status_code in (200, 201, 204)
    except Exception:
        return False


class Cpa401Checker:
    def __init__(self, base_url: str, token: str, target_type: str = "codex", user_agent: str = DEFAULT_MGMT_UA):
        self.base_url = (base_url or "").rstrip("/")
        self.token = token
        self.target_type = target_type
        self.user_agent = user_agent

    def fetch_auth_files(self, timeout: int = 15):
        resp = requests.get(f"{self.base_url}/v0/management/auth-files", headers=_mgmt_headers(self.token), timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("files") if isinstance(data, dict) else []) or []

    async def probe_401_async(self, workers: int = 20, timeout: int = 10, retries: int = 1):
        if aiohttp is None:
            raise RuntimeError("需要安装 aiohttp: pip install aiohttp")
        files = self.fetch_auth_files(timeout)
        candidates = [f for f in files if _get_item_type(f).lower() == self.target_type.lower()]
        if not candidates:
            return {"total": len(files), "candidates": 0, "invalid_401": [], "errors": []}

        semaphore = asyncio.Semaphore(max(1, workers))
        connector = aiohttp.TCPConnector(limit=max(1, workers))
        client_timeout = aiohttp.ClientTimeout(total=max(1, timeout))
        errors = []

        async def probe_one(session, item):
            auth_index = item.get("auth_index")
            name = item.get("name") or item.get("id")
            if not auth_index:
                return {"name": name, "auth_index": auth_index, "invalid_401": False}
            account_id = _extract_account_id(item)
            header = {"Authorization": "Bearer $TOKEN$", "Content-Type": "application/json", "User-Agent": self.user_agent}
            if account_id:
                header["Chatgpt-Account-Id"] = account_id
            payload = {"authIndex": auth_index, "method": "GET", "url": "https://chatgpt.com/backend-api/wham/usage", "header": header}
            for attempt in range(retries + 1):
                try:
                    async with semaphore:
                        async with session.post(
                            f"{self.base_url}/v0/management/api-call",
                            headers={**_mgmt_headers(self.token), "Content-Type": "application/json"},
                            json=payload,
                            timeout=timeout,
                        ) as resp:
                            text = await resp.text()
                            if resp.status >= 400:
                                raise RuntimeError(f"HTTP {resp.status}: {text[:200]}")
                            data = _safe_json(text)
                            sc = data.get("status_code")
                            return {"name": name, "auth_index": auth_index, "invalid_401": sc == 401}
                except Exception as e:
                    if attempt >= retries:
                        errors.append({"name": name, "auth_index": auth_index, "error": str(e)})
                        return {"name": name, "auth_index": auth_index, "invalid_401": False}
            return {"name": name, "auth_index": auth_index, "invalid_401": False}

        invalid = []
        async with aiohttp.ClientSession(connector=connector, timeout=client_timeout, trust_env=True) as session:
            tasks = [asyncio.create_task(probe_one(session, item)) for item in candidates]
            for task in asyncio.as_completed(tasks):
                r = await task
                if r.get("invalid_401"):
                    invalid.append(r)

        return {"total": len(files), "candidates": len(candidates), "invalid_401": invalid, "errors": errors}

    async def delete_by_name_async(self, names, workers: int = 20, timeout: int = 10):
        if aiohttp is None:
            raise RuntimeError("需要安装 aiohttp: pip install aiohttp")
        if not names:
            return {"deleted_ok": 0, "deleted_fail": 0}

        semaphore = asyncio.Semaphore(max(1, workers))
        connector = aiohttp.TCPConnector(limit=max(1, workers))
        client_timeout = aiohttp.ClientTimeout(total=max(1, timeout))

        async def delete_one(session, name: str):
            if not name:
                return False
            encoded = urllib.parse.quote(name, safe="")
            try:
                async with semaphore:
                    async with session.delete(
                        f"{self.base_url}/v0/management/auth-files?name={encoded}",
                        headers=_mgmt_headers(self.token),
                        timeout=timeout,
                    ) as resp:
                        text = await resp.text()
                        data = _safe_json(text)
                        return resp.status == 200 and data.get("status") == "ok"
            except Exception:
                return False

        deleted_ok = 0
        deleted_fail = 0
        async with aiohttp.ClientSession(connector=connector, timeout=client_timeout, trust_env=True) as session:
            tasks = [asyncio.create_task(delete_one(session, name)) for name in names]
            for task in asyncio.as_completed(tasks):
                if await task:
                    deleted_ok += 1
                else:
                    deleted_fail += 1

        return {"deleted_ok": deleted_ok, "deleted_fail": deleted_fail}

    def probe_401_sync(self, workers: int = 20, timeout: int = 10, retries: int = 1):
        return asyncio.run(self.probe_401_async(workers, timeout, retries))

    def delete_by_name_sync(self, names, workers: int = 20, timeout: int = 10):
        return asyncio.run(self.delete_by_name_async(names, workers, timeout))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpa-base-url", default="http://localhost:8317", help="CPA 基础地址")
    parser.add_argument("--cpa-token", required=True, help="CPA 管理 token (Bearer)")
    parser.add_argument("--workers", type=int, default=20, help="并发探测数")
    parser.add_argument("--timeout", type=int, default=12, help="请求超时")
    parser.add_argument("--retries", type=int, default=1, help="重试次数")
    parser.add_argument("--output", default="", help="输出 JSON 文件路径")
    parser.add_argument("--delete", action="store_true", help="删除检测到的 401 凭证")
    parser.add_argument("--upload-dir", default="", help="批量上传 JSON 文件的目录")
    args = parser.parse_args()

    base_url = (args.cpa_base_url or "").rstrip("/")

    if args.upload_dir:
        upload_dir = Path(args.upload_dir).expanduser().resolve()
        if not upload_dir.exists() or not upload_dir.is_dir():
            raise SystemExit(f"目录不存在: {upload_dir}")
        files = sorted(upload_dir.glob("*.json"))
        uploaded_ok = 0
        uploaded_fail = 0
        for path in files:
            if _upload_one_json(base_url, args.cpa_token, path):
                uploaded_ok += 1
            else:
                uploaded_fail += 1
        print(f"uploaded_ok={uploaded_ok} uploaded_fail={uploaded_fail}")
        return

    checker = Cpa401Checker(base_url, args.cpa_token)
    result = checker.probe_401_sync(args.workers, args.timeout, args.retries)

    invalid = result.get("invalid_401", [])
    print(f"total={result.get('total')} candidates={result.get('candidates')} invalid_401={len(invalid)} errors={len(result.get('errors', []))}")

    for item in invalid:
        print(f"401: name={item.get('name')} auth_index={item.get('auth_index')}")

    if args.delete and invalid:
        names = [item.get("name") for item in invalid if item.get("name")]
        delete_result = checker.delete_by_name_sync(names, args.workers, args.timeout)
        print(f"deleted_ok={delete_result.get('deleted_ok')} deleted_fail={delete_result.get('deleted_fail')}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
