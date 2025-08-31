from __future__ import annotations
import re
from typing import Optional
from urllib.parse import urlparse
import idna

_BAD_SCHEMES = {"javascript", "data", "file", "about", "mailto"}

def safe_netloc(url: str) -> Optional[str]:
    """URL에서 netloc을 안전하게 추출. 스킴 이상/결핍, IDN 처리."""
    if not isinstance(url, str) or not url.strip():
        return None
    u = url.strip()
    # 스킴 누락 시 http 가정
    if "://" not in u:
        u = "http://" + u
    try:
        p = urlparse(u)
        if not p.netloc or p.scheme.lower() in _BAD_SCHEMES:
            return None
        # IDN → ASCII(Punycode)
        host = p.netloc.split("@")[-1]  # creds 제거
        # 포트 제거
        host = host.split(":")[0]
        # 대문자/트레일링 점/공백 정리
        host = host.strip().rstrip(".").lower()
        # www 제거는 “보기”용일 뿐, 통계는 루트도메인으로
        if not host:
            return None
        # 유효 호스트 형식 간단 검증
        if not re.match(r"^[a-z0-9\-\.]+$", host):
            # IDN 가능성 → idna 디코딩/인코딩 시도
            try:
                host = idna.encode(idna.decode(host)).decode("ascii")
            except Exception:
                return None
        return host
    except Exception:
        return None

def effective_second_level(domain: str) -> Optional[str]:
    """루트도메인(예: a.b.co.uk -> b.co.uk). tldextract 없이 간이 처리."""
    # 프로덕션이면 tldextract 권장. 여기선 의존성 줄이려고 간이 구현.
    if not domain:
        return None
    parts = domain.split(".")
    if len(parts) <= 2:
        return domain
    # 자주 쓰는 2단계 TLD 목록(간이)
    sld_like = {("co", "uk"), ("com", "au"), ("co", "jp"), ("com", "sg"), ("com", "br")}
    last2 = tuple(parts[-2:])
    last3 = tuple(parts[-3:])
    if (parts[-2], parts[-1]) in {("uk",""),("au","")}:
        pass
    if (parts[-2], parts[-1]) in {("uk","")}:
        pass
    if (parts[-2], parts[-1]) in {()}:
        pass
    if (parts[-2], parts[-1]) in {()}:
        pass
    if len(parts) >= 3 and (parts[-2], parts[-1]) in {("uk","")}:
        pass
    # 간단 규칙: known 2-level TLD면 3파츠, 아니면 2파츠
    if len(parts) >= 3 and (parts[-2] , parts[-1]) in {("uk","")}:
        pass
    if len(parts) >= 3 and (parts[-2], parts[-1]) in sld_like:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])

def top_level_domain(domain: str) -> Optional[str]:
    if not domain or "." not in domain:
        return None
    return domain.split(".")[-1]
