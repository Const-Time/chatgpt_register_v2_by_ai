"""
yyds-mail 邮箱客户端适配模块
"""

import random
import re
import string
import sys
import time

import requests


class SkymailClient:
    """兼容旧接口的 yyds-mail 邮箱客户端。"""

    def __init__(self, api_key, api_base=None, proxy=None, domains=None):
        """
        初始化 yyds-mail 客户端。

        Args:
            api_key: yyds-mail API Key
            api_base: API 基础地址
            proxy: 代理地址（可选）
            domains: 可选域名列表
        """
        self.api_key = (api_key or "").strip()
        self.api_base = (api_base or "https://maliapi.215.im").rstrip("/")
        self.proxy = proxy
        self.api_token = None
        self.domains = [domain for domain in (domains or []) if isinstance(domain, str) and domain.strip()]
        self._used_codes = set()
        self._mail_tokens = {}
        self._account_ids = {}

    def _build_session(self):
        session = requests.Session()
        if self.proxy:
            session.proxies = {"http": self.proxy, "https": self.proxy}
        return session

    def _api_headers(self, use_api_key=False, bearer_token=None):
        headers = {"Accept": "application/json"}
        if use_api_key:
            headers["X-API-Key"] = self.api_token
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        return headers

    def _fetch_available_domains(self):
        session = self._build_session()
        res = session.get(
            f"{self.api_base}/v1/domains",
            headers=self._api_headers(),
            timeout=15,
            verify=False
        )

        if res.status_code != 200:
            raise Exception(f"获取域名失败: {res.status_code} - {res.text[:200]}")

        data = res.json()
        if not data.get("success"):
            raise Exception(data.get("error") or "获取域名失败")

        domains = []
        for item in data.get("data", []):
            domain = item.get("domain") if isinstance(item, dict) else None
            if domain:
                domains.append(domain)
        return domains

    def _normalize_message(self, message):
        text = message.get("text") or ""
        html = message.get("html") or []
        if isinstance(html, list):
            html_content = "\n".join(part for part in html if isinstance(part, str))
        elif isinstance(html, str):
            html_content = html
        else:
            html_content = ""

        content = text or html_content
        normalized = dict(message)
        normalized["emailId"] = message.get("id") or message.get("emailId")
        normalized["content"] = content
        normalized["text"] = text or html_content
        return normalized

    def _fetch_message_detail(self, message_id, token=None):
        session = self._build_session()
        headers = self._api_headers(use_api_key=not token, bearer_token=token)
        res = session.get(
            f"{self.api_base}/v1/messages/{message_id}",
            headers=headers,
            timeout=15,
            verify=False
        )

        if res.status_code != 200:
            return None

        data = res.json()
        if not data.get("success"):
            return None
        detail = data.get("data") or {}
        if not isinstance(detail, dict):
            return None
        return self._normalize_message(detail)

    def generate_token(self):
        """兼容旧调用，直接校验并缓存 yyds-mail API Key。"""
        if not self.api_key:
            print("⚠️ 未配置 yyds-mail API Key")
            return None

        self.api_token = self.api_key
        print("✅ 已加载 yyds-mail API Key")
        return self.api_token

    def create_temp_email(self):
        """
        创建 yyds-mail 临时邮箱。

        Returns:
            tuple: (email, token) - 邮箱地址和临时 token
        """
        if not self.api_token:
            raise Exception("YYDSMAIL_API_KEY 未设置，无法创建临时邮箱")

        try:
            available_domains = self.domains or self._fetch_available_domains()
            domain = random.choice(available_domains) if available_domains else None
            prefix_length = random.randint(6, 10)
            prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=prefix_length))

            payload = {}
            if domain:
                payload["domain"] = domain
                payload["address"] = prefix

            session = self._build_session()
            res = session.post(
                f"{self.api_base}/v1/accounts",
                json=payload,
                headers=self._api_headers(use_api_key=True),
                timeout=15,
                verify=False
            )

            if res.status_code != 200:
                raise Exception(f"{res.status_code} - {res.text[:200]}")

            data = res.json()
            if not data.get("success"):
                raise Exception(data.get("error") or "创建临时邮箱失败")

            account = data.get("data") or {}
            email = account.get("address")
            temp_token = account.get("token")
            account_id = account.get("id")

            if not email or not temp_token:
                raise Exception(f"响应缺少邮箱或 token: {account}")

            self._mail_tokens[email] = temp_token
            if account_id:
                self._account_ids[email] = account_id

            return email, temp_token

        except Exception as e:
            raise Exception(f"yyds-mail 创建邮箱失败: {e}")

    def fetch_emails(self, email):
        """
        从 yyds-mail 获取邮件列表及详情。

        Args:
            email: 邮箱地址

        Returns:
            list: 邮件列表
        """
        try:
            temp_token = self._mail_tokens.get(email)
            session = self._build_session()
            headers = self._api_headers(use_api_key=not temp_token, bearer_token=temp_token)
            res = session.get(
                f"{self.api_base}/v1/messages",
                params={"address": email, "limit": 10},
                headers=headers,
                timeout=15,
                verify=False
            )

            if res.status_code != 200:
                return []

            data = res.json()
            if not data.get("success"):
                return []

            messages = (data.get("data") or {}).get("messages", [])
            details = []
            for item in messages:
                if not isinstance(item, dict):
                    continue
                message_id = item.get("id")
                if not message_id:
                    continue

                detail = self._fetch_message_detail(message_id, token=temp_token)
                if detail:
                    details.append(detail)

            return details
            return []
        except Exception:
            return []

    def extract_verification_code(self, content):
        """从邮件内容提取6位验证码"""
        if not content:
            return None

        patterns = [
            r"Verification code:?\s*(\d{6})",
            r"code is\s*(\d{6})",
            r"代码为[:：]?\s*(\d{6})",
            r"验证码[:：]?\s*(\d{6})",
            r">\s*(\d{6})\s*<",
            r"(?<![#&])\b(\d{6})\b",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for code in matches:
                if code == "177010":  # 已知误判
                    continue
                return code
        return None

    def wait_for_verification_code(self, email, timeout=30, exclude_codes=None):
        """
        等待验证邮件并提取验证码
        
        Args:
            email: 邮箱地址
            timeout: 超时时间（秒）
            exclude_codes: 要排除的验证码集合（避免重复使用）
            
        Returns:
            str: 验证码，失败返回 None
        """
        if exclude_codes is None:
            exclude_codes = set()
        
        # 合并实例级别的已使用验证码
        if not hasattr(self, '_used_codes'):
            self._used_codes = set()
        all_exclude_codes = exclude_codes | self._used_codes
        
        print(f"  ⏳ 等待验证码 (最大 {timeout}s)...")
        
        start = time.time()
        last_email_ids = set()
        
        # 立即开始轮询
        while time.time() - start < timeout:
            emails = self.fetch_emails(email)
            
            if emails:
                for item in emails:
                    if not isinstance(item, dict):
                        continue
                    
                    email_id = item.get("emailId")
                    if not email_id or email_id in last_email_ids:
                        continue
                    
                    # 记录这个邮件 ID
                    last_email_ids.add(email_id)
                    
                    # 提取验证码
                    content = item.get("content") or item.get("text") or ""
                    code = self.extract_verification_code(content)
                    
                    if code and code not in all_exclude_codes:
                        print(f"  ✅ 验证码: {code}")
                        # 记录已使用的验证码
                        self._used_codes.add(code)
                        return code
            
            # 动态等待时间：前10秒快速轮询（0.5秒），之后慢速轮询（2秒）
            elapsed = time.time() - start
            if elapsed < 10:
                time.sleep(0.5)
            else:
                time.sleep(2)
        
        print("  ⏰ 等待验证码超时")
        return None


def init_skymail_client(config):
    """
    初始化 yyds-mail 客户端。

    Args:
        config: 配置字典

    Returns:
        SkymailClient: 初始化好的客户端实例
    """
    api_key = config.get("yydsmail_api_key", "") or config.get("skymail_admin_password", "")
    api_base = config.get("yydsmail_api_base", "") or config.get("skymail_api_base", "")
    proxy = config.get("proxy", "")
    domains = config.get("yydsmail_domains", None)
    if domains is None:
        domains = config.get("skymail_domains", None)

    if not api_key:
        print("❌ 错误: 未配置 yyds-mail API Key")
        print("   请在 config.json 中设置 yydsmail_api_key")
        sys.exit(1)

    if domains is not None and not isinstance(domains, list):
        print("❌ 错误: yydsmail_domains 必须为数组")
        sys.exit(1)

    if isinstance(domains, list) and len(domains) == 0:
        domains = None

    client = SkymailClient(api_key, api_base=api_base, proxy=proxy, domains=domains)

    print(f"🔑 正在加载 yyds-mail API Key (API: {client.api_base})...")
    if domains:
        print(f"📧 预设域名: {', '.join(domains)}")
    else:
        print("📧 未预设域名，将在运行时自动获取公开域名")
    token = client.generate_token()

    if not token:
        print("❌ API Key 加载失败，无法继续")
        sys.exit(1)

    return client
