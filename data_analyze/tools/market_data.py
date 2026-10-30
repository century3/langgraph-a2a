import requests


def http_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    return session


def normalize_code(code: str) -> str:
    digits = "".join(ch for ch in str(code) if ch.isdigit())
    return digits.zfill(6)[-6:] if digits else ""


def normalize_codes(stock_codes) -> list[str]:
    if stock_codes is None:
        return []
    if isinstance(stock_codes, str):
        stock_codes = stock_codes.replace("，", ",").replace(" ", ",").split(",")
    return [code for code in (normalize_code(item) for item in stock_codes) if len(code) == 6]


def market_symbol(code: str) -> str:
    if code.startswith(("6", "9")):
        return f"sh{code}"
    if code.startswith(("4", "8")):
        return f"bj{code}"
    return f"sz{code}"


def exchange_code(code: str) -> str:
    if code.startswith(("6", "9")):
        return f"SH{code}"
    if code.startswith(("4", "8")):
        return f"BJ{code}"
    return f"SZ{code}"


def fetch_kline(code: str, count: int = 250) -> list[list[str]]:
    symbol = market_symbol(code)
    response = http_session().get(
        "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",
        params={"param": f"{symbol},day,,,{count},qfq"},
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()["data"][symbol]
    return payload.get("qfqday") or payload.get("day") or []


def fetch_financials(code: str) -> dict:
    response = http_session().get(
        "https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/ZYZBAjaxNew",
        params={"type": "0", "code": exchange_code(code)},
        timeout=12,
        headers={"Referer": "https://emweb.securities.eastmoney.com/"},
    )
    response.raise_for_status()
    rows = response.json().get("data") or []
    return rows[0] if rows else {}
