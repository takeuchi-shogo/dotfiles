#!/usr/bin/env python3
"""sources.py — sources-ledger.jsonl の管理 (Phase 2)。

情報源を構造化記録する registry。Phase 1 の sources.txt (フラットな feed URL 列) を
seed として bootstrap し、status=active な情報源の収集対象を提供する。
採用実績 (adoption-ledger.jsonl) から score/last_adopted を materialized view として
再計算する (正本は adoption-ledger、ここは派生スナップショット)。

設計決定 (docs/plans active 2026-06-04 Phase 2):
  D1: type:web の進化単位 = feed URL (domain ではない)。
      → adoption-ledger の source_id = 記事を収集した feed URL = この row の value。
  D2: type:keyword はスキーマ上サポートするが Phase 2 は seed しない
      (収集配線は Phase 3+)。
  D4: status は変更しない (昇格降格は Phase 3)。score/last_adopted のみ refresh で更新。

スキーマ (1 行 1 JSON):
  {"type":"web|keyword","value":"<feed URL|keyword>","added_date":"YYYY-MM-DD",
   "score":<float>,"last_adopted":"YYYY-MM-DD"|null,"status":"active|candidate|retired"}

サブコマンド:
  bootstrap   sources.txt を seed に sources-ledger を初期化/マージ
  list-active status=active な value を 1 行ずつ出力 (収集対象)
  refresh     adoption から score/last_adopted を再計算 (materialized view)
  prune       窓外の古い adoption 行を archive へ退避

pure logic (bootstrap_rows/list_active/refresh_rows/prune_lines) は副作用を持たず、
入力の行リストと引数のみに依存する (CLI ラッパが I/O を担う)。
"""

from __future__ import annotations

import argparse
import contextlib
import ipaddress
import json
import os
import sys
import tempfile
from datetime import date, datetime, timedelta

VALID_STATUS = {"active", "candidate", "retired"}


def _parse_date(s: object) -> date | None:
    """YYYY-MM-DD を date に。失敗時 None (malformed line tolerant)。"""
    if not isinstance(s, str):
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _token_as_int(token: str) -> int | None:
    """1 トークンを decimal/hex/octal 整数として解釈。失敗時 None。"""
    low = token.lower()
    try:
        if low.startswith("0x"):
            return int(low, 16)
        if low.startswith("0") and len(low) > 1 and low.isdigit():
            return int(low, 8)
        if low.isdigit():
            return int(low, 10)
    except ValueError:
        return None
    return None


def _inet_aton_int(host: str) -> int | None:
    """host を curl(inet_aton) と同様に packed IPv4 整数へ。非数値/範囲外は None。

    inet_aton は 1-4 個の dec/hex/oct トークンを受理し、末尾トークンが残りオクテットを
    埋める短縮形 (例 `127.1`=127.0.0.1, `0x7f.1`) を許す。Python の ipaddress は
    これらを拒否するため curl との parser 乖離で SSRF guard を抜けられる
    (security-reviewer HIGH)。ここで curl と同じ規則で packing して塞ぐ。
    """
    parts = host.split(".")
    if not (1 <= len(parts) <= 4):
        return None
    vals = []
    for p in parts:
        v = _token_as_int(p)
        if v is None or v < 0:
            return None
        vals.append(v)
    *lead, last = vals
    if any(v > 0xFF for v in lead):
        return None
    max_last = 1 << (8 * (4 - len(lead)))
    if last >= max_last:
        return None
    result = last
    for i, v in enumerate(lead):
        result |= v << (8 * (3 - i))
    return result


def _coerce_host_to_ip(host: str) -> object | None:
    """host を IP アドレスへ正規化。IP リテラルでなければ None (= 通常ホスト名)。"""
    with contextlib.suppress(ValueError):
        return ipaddress.ip_address(host)
    val = _inet_aton_int(host)
    if val is not None and 0 <= val <= 0xFFFFFFFF:
        try:
            return ipaddress.ip_address(val)
        except ValueError:
            return None
    return None


def _host_is_blocked(host: str) -> bool:
    """host が到達禁止アドレス (private/loopback/link-local/reserved 等) を指すか。

    curl(inet_aton) が解釈する decimal/hex/octal/dotted(短縮形含む)/IPv6/IPv4-mapped を
    正規化して判定する。文字列 prefix 一致では `2130706433`(=127.0.0.1) や `127.1` 等で
    bypass されるため ipaddress で canonical 化する (security-reviewer HIGH 指摘)。
    通常ホスト名は False (DNS 解決時 SSRF は範囲外、Phase 3 で fetch-time pin 検討)。
    """
    ip = _coerce_host_to_ip(host)
    if ip is None:
        return False
    targets = [ip]
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        targets.append(mapped)
    return any(
        a.is_private
        or a.is_loopback
        or a.is_link_local
        or a.is_reserved
        or a.is_unspecified
        or a.is_multicast
        for a in targets
    )


def is_safe_feed_url(url: str) -> bool:
    """SSRF guard: https?:// のみ + private/link-local/loopback 等の IP を拒否。

    Phase 2 セキュリティ前提 (security-reviewer 指摘): sources-ledger に外部由来 URL が
    動的投入される前に host の private/link-local denylist を入れる (defense-in-depth)。
    bootstrap の chokepoint で適用し、Phase 3 の自動昇格もこの関数を通す前提。
    """
    if not isinstance(url, str) or not url.lower().startswith(("http://", "https://")):
        return False
    rest = url.split("://", 1)[1]
    # authority = scheme 後の最初の '/' '?' '#' まで。userinfo/port は後段で除く。
    authority = rest.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]
    host = authority.split("@")[-1]  # userinfo 除去
    # port 除去 ([::1]:8080 や host:443)。IPv6 角括弧も剥がす。
    if host.startswith("["):
        host = host[1 : host.find("]")] if "]" in host else host[1:]
    elif host.count(":") == 1:
        host = host.rsplit(":", 1)[0]
    host = host.strip().lower()
    if not host or host == "localhost":
        return False
    return not _host_is_blocked(host)


def parse_seed(text: str) -> list[str]:
    """sources.txt をパースし安全な feed URL を順序保持で返す。

    run-tech-researcher.sh と同じ規約: 行内 '#' 以降はコメント、前後空白 trim、
    空行スキップ、https?:// のみ。さらに private/link-local を拒否 (is_safe_feed_url)。
    """
    urls: list[str] = []
    for line in text.splitlines():
        url = line.split("#", 1)[0].strip()
        if not url:
            continue
        if not is_safe_feed_url(url):
            print(f"[sources] skip unsafe/non-http seed: {url}", file=sys.stderr)
            continue
        urls.append(url)
    return urls


def _parse_ledger(lines: list[str]) -> list[dict]:
    """sources-ledger 行を dict のリストへ。malformed/必須欠落行は skip + warn。"""
    rows: list[dict] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            print(f"[sources] skip malformed ledger line: {line[:80]}", file=sys.stderr)
            continue
        if not isinstance(rec, dict):
            continue
        typ, val = rec.get("type"), rec.get("value")
        if typ not in {"web", "keyword"} or not isinstance(val, str) or not val:
            print(
                f"[sources] skip invalid ledger row (type/value): {line[:80]}",
                file=sys.stderr,
            )
            continue
        rows.append(rec)
    return rows


def bootstrap_rows(
    ledger_lines: list[str], seed_urls: list[str], *, asof: date
) -> list[dict]:
    """既存 ledger 行を保持しつつ、未登録の seed URL を type:web で追加 (idempotent)。

    既存行の status/score/last_adopted は維持する (seed 再実行で進化結果を潰さない)。
    """
    rows = _parse_ledger(ledger_lines)
    known = {(r["type"], r["value"]) for r in rows}
    asof_s = asof.isoformat()
    for url in seed_urls:
        key = ("web", url)
        if key in known:
            continue
        rows.append(
            {
                "type": "web",
                "value": url,
                "added_date": asof_s,
                "score": 0.0,
                "last_adopted": None,
                "status": "active",
            }
        )
        known.add(key)
    return rows


def list_active(
    ledger_lines: list[str], *, type_filter: str | None = None
) -> list[str]:
    """status=active な value を順序保持で返す。type_filter 指定時はその type のみ。"""
    out: list[str] = []
    for r in _parse_ledger(ledger_lines):
        if r.get("status") != "active":
            continue
        if type_filter is not None and r.get("type") != type_filter:
            continue
        out.append(r["value"])
    return out


def _max_date_str(a: str | None, b: str | None) -> str | None:
    """None を最小として 2 つの YYYY-MM-DD 文字列の大きい方を返す。"""
    cands = [x for x in (a, b) if isinstance(x, str) and _parse_date(x) is not None]
    return max(cands) if cands else None


def refresh_rows(
    ledger_lines: list[str], adoption_lines: list[str], *, asof: date, days: int
) -> list[dict]:
    """adoption-ledger から source_id (=value) 別に score/last_adopted を再計算。

    score = 直近 days 日の採用率 (adopted/total, 観測無しは 0.0) — 補助指標 (Task 2.3)。
    last_adopted = adoption 全期間で adopted=true の最大日 (既存値とで新しい方を採用)。
    status は変更しない (D4)。adoption に居るが ledger に無い source_id は無視 (E7)。
    Phase 1 行 (source_id 欠落) は属性付けできず無視する (null-tolerant)。
    type=web のみ更新する。keyword (Phase 3+) は feed URL の source_id と対応せず、
    更新すると score を毎回 0.0 にリセットしてしまうため触らない。
    """
    rows = _parse_ledger(ledger_lines)
    cutoff = asof - timedelta(days=days - 1)
    window: dict[str, list[int]] = {}  # source_id -> [adopted, total]
    last_adopted: dict[str, str] = {}  # source_id -> max adopted date str
    for line in adoption_lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        sid = rec.get("source_id")
        if not isinstance(sid, str) or not sid:
            continue
        d = _parse_date(rec.get("date"))
        if d is None:
            continue
        adopted = rec.get("adopted") is True
        if cutoff <= d <= asof:
            b = window.setdefault(sid, [0, 0])
            b[1] += 1
            if adopted:
                b[0] += 1
        if adopted:
            ds = d.isoformat()
            if sid not in last_adopted or ds > last_adopted[sid]:
                last_adopted[sid] = ds
    for r in rows:
        if r.get("type") != "web":
            continue
        sid = r["value"]  # D1: web の join キーは value (feed URL)
        b = window.get(sid)
        r["score"] = round(b[0] / b[1], 4) if b and b[1] else 0.0
        r["last_adopted"] = _max_date_str(r.get("last_adopted"), last_adopted.get(sid))
    return rows


def prune_lines(
    adoption_lines: list[str], *, asof: date, keep_days: int
) -> tuple[list[str], list[str]]:
    """adoption 行を (kept, archived) に分割。kept は直近 keep_days 窓内 + 日付不明行。

    集計は 30 日窓なので keep_days(既定90)外の行は集計に無影響 → archive へ退避可。
    日付パース不能行は保守的に kept 側へ残す (取りこぼし防止)。
    """
    cutoff = asof - timedelta(days=keep_days - 1)
    kept: list[str] = []
    archived: list[str] = []
    for line in adoption_lines:
        s = line.strip()
        if not s:
            continue
        try:
            rec = json.loads(s)
        except (json.JSONDecodeError, ValueError):
            kept.append(s)
            continue
        d = _parse_date(rec.get("date"))
        if d is None or d >= cutoff:
            kept.append(s)
        else:
            archived.append(s)
    return kept, archived


# --- I/O ヘルパ (CLI 専用、pure logic とは分離) ---


def _read_lines(path: str) -> list[str]:
    try:
        with open(path, encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []


def _write_jsonl_atomic(path: str, rows: list[dict]) -> None:
    """temp + os.replace で atomic に書き戻す (中断時の半端書き込み防止)。"""
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".sources-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):  # tmp 後始末。元例外を再送出。
            os.unlink(tmp)
        raise


def _resolve_asof(raw: str | None) -> date | None:
    """--asof 未指定は today、指定ありで不正なら None (呼び出し側で error 終了)。

    aggregate.py と挙動を揃える。不正値の today silent fallback は added_date 等を
    意図しない日付で記録し追跡不能にするため、明示エラーにする。
    """
    if raw is None:
        return date.today()
    return _parse_date(raw)


def _cmd_bootstrap(args: argparse.Namespace) -> int:
    asof = _resolve_asof(args.asof)
    if asof is None:
        print(f"ERROR: invalid --asof: {args.asof}", file=sys.stderr)
        return 2
    try:
        with open(args.seed, encoding="utf-8") as f:
            seed_text = f.read()
    except FileNotFoundError:
        print(f"ERROR: seed not found: {args.seed}", file=sys.stderr)
        return 2
    seed_urls = parse_seed(seed_text)
    rows = bootstrap_rows(_read_lines(args.ledger), seed_urls, asof=asof)
    _write_jsonl_atomic(args.ledger, rows)
    return 0


def _cmd_list_active(args: argparse.Namespace) -> int:
    for v in list_active(_read_lines(args.ledger), type_filter=args.type):
        sys.stdout.write(v + "\n")
    return 0


def _cmd_refresh(args: argparse.Namespace) -> int:
    asof = _resolve_asof(args.asof)
    if asof is None:
        print(f"ERROR: invalid --asof: {args.asof}", file=sys.stderr)
        return 2
    if args.days < 1:
        print("ERROR: --days must be >= 1", file=sys.stderr)
        return 2
    rows = refresh_rows(
        _read_lines(args.ledger), _read_lines(args.adoption), asof=asof, days=args.days
    )
    _write_jsonl_atomic(args.ledger, rows)
    return 0


def _cmd_prune(args: argparse.Namespace) -> int:
    asof = _resolve_asof(args.asof)
    if asof is None:
        print(f"ERROR: invalid --asof: {args.asof}", file=sys.stderr)
        return 2
    if args.keep_days < 1:
        print("ERROR: --keep-days must be >= 1", file=sys.stderr)
        return 2
    kept, archived = prune_lines(
        _read_lines(args.adoption), asof=asof, keep_days=args.keep_days
    )
    if not archived:
        return 0  # 退避対象なし: 何も触らない
    # archive を先に append し、成功後に本体を kept のみへ書き戻す (取りこぼし防止)。
    with open(args.archive, "a", encoding="utf-8") as f:
        for s in archived:
            f.write(s + "\n")
    fd, tmp = tempfile.mkstemp(
        dir=os.path.dirname(args.adoption) or ".", prefix=".adopt-", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for s in kept:
                f.write(s + "\n")
        os.replace(tmp, args.adoption)
    except BaseException:
        with contextlib.suppress(OSError):  # tmp 後始末。元例外を再送出。
            os.unlink(tmp)
        raise
    print(f"[sources] pruned {len(archived)} rows -> {args.archive}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_boot = sub.add_parser(
        "bootstrap", help="sources.txt を seed に ledger を初期化/マージ"
    )
    p_boot.add_argument("--seed", required=True)
    p_boot.add_argument("--ledger", required=True)
    p_boot.add_argument("--asof", default=None)
    p_boot.set_defaults(func=_cmd_bootstrap)

    p_list = sub.add_parser("list-active", help="status=active な value を出力")
    p_list.add_argument("--ledger", required=True)
    p_list.add_argument("--type", default=None, choices=["web", "keyword"])
    p_list.set_defaults(func=_cmd_list_active)

    p_ref = sub.add_parser("refresh", help="adoption から score/last_adopted を再計算")
    p_ref.add_argument("--ledger", required=True)
    p_ref.add_argument("--adoption", required=True)
    p_ref.add_argument("--asof", default=None)
    p_ref.add_argument("--days", type=int, default=30)
    p_ref.set_defaults(func=_cmd_refresh)

    p_pr = sub.add_parser("prune", help="窓外の古い adoption 行を archive へ退避")
    p_pr.add_argument("--adoption", required=True)
    p_pr.add_argument("--archive", required=True)
    p_pr.add_argument("--asof", default=None)
    p_pr.add_argument("--keep-days", type=int, default=90)
    p_pr.set_defaults(func=_cmd_prune)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
