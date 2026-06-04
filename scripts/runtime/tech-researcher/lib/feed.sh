#!/usr/bin/env bash
# feed.sh — Atom/RSS の (url, title) ペア抽出 + サニタイズ。
# 出自: .config/claude/scripts/runtime/auto-morning-briefing.sh の
#       sanitize_title をコピー / extract_feed_titles を item 単位ペア抽出へ拡張 (rule-of-three 2 例目)。
# 差分: (1) channel/feed 自身の <title> を拾わぬよう item/entry 単位に分割し title+link をペアで取る。
#       (2) 日本語フィードで tr が "Illegal byte sequence" を出すため tr に LC_ALL=C を付与。

TECH_RESEARCHER_TITLE_MAX="${TECH_RESEARCHER_TITLE_MAX:-200}"

# entity decode 順序: lt/gt/quot/apos を先、&amp; を最後 (二重エンコード &amp;lt; を `<` に展開しない)
sanitize_title() {
    local input="$1"
    local max_len="${2:-$TECH_RESEARCHER_TITLE_MAX}"
    printf '%s' "$input" \
        | LC_ALL=C tr -d '\n\r\t' \
        | sed 's/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g; s/&#39;/'"'"'/g; s/&apos;/'"'"'/g; s/&amp;/\&/g' \
        | cut -c1-"$max_len"
}

# extract_feed_items <raw_xml> [head_n=10]
# 各 <item>(RSS) / <entry>(Atom) から最初の title と link を取り `url<TAB>title` を 1 行ずつ出力。
# item 単位に分割するため channel/feed 自体の title は混入しない。
# link 解決順: Atom <link href="..."/> → RSS <link>..</link> → <guid>..</guid>。
# chunk 群を一旦変数に確保してから走査する: 呼び出し側が set -e + pipefail のとき
# `grep | head | while` だと head 早期クローズで grep が SIGPIPE(141) → pipefail で
# パイプライン全体が非ゼロ → set -e が中断する。`$(... | head)` + `|| true` で吸収し、
# while は here-string から読むことで SIGPIPE を回避する。
extract_feed_items() {
    local raw="$1" head_n="${2:-10}"
    local chunks
    chunks=$(printf '%s' "$raw" | LC_ALL=C tr '\n' ' ' \
        | LC_ALL=C sed -E 's#<(item|entry)[ >]#\n<\1 #g' \
        | LC_ALL=C grep -E '^<(item|entry)' \
        | head -n "$head_n") || true
    [[ -z "$chunks" ]] && return 0
    # 各 $(... | head) には `|| true` を付す: 1 chunk に複数 <link> 等があると head 早期
    # クローズで grep が SIGPIPE → pipefail で非ゼロ → set -e 中断、を防ぐ。
    local title url
    while IFS= read -r chunk; do
        [[ -z "$chunk" ]] && continue
        # 既知の限界: CDATA 内に ASCII `]` を含む title は `[^]]*` が途中で止まり取得失敗
        # → その記事はスキップ (非系統的 drop で計測は歪まない)。日本語は全角【】が主で実害小。
        title=$(printf '%s' "$chunk" \
            | LC_ALL=C grep -oE '<title[^>]*>(<!\[CDATA\[[^]]*\]\]>|[^<]*)</title>' \
            | head -1 \
            | sed -E 's|<title[^>]*>(<!\[CDATA\[)?||; s|(\]\]>)?</title>.*||' \
            | LC_ALL=C tr -d '<>' \
            | sed 's/^[[:space:]]*//; s/[[:space:]]*$//') || true
        url=$(printf '%s' "$chunk" | LC_ALL=C grep -oE '<link[^>]*href="[^"]+"' | head -1 | sed -E 's|.*href="([^"]+)".*|\1|') || true
        [[ -z "$url" ]] && { url=$(printf '%s' "$chunk" | LC_ALL=C grep -oE '<link>[^<]+</link>' | head -1 | sed -E 's|</?link>||g') || true; }
        [[ -z "$url" ]] && { url=$(printf '%s' "$chunk" | LC_ALL=C grep -oE '<guid[^>]*>[^<]+</guid>' | head -1 | sed -E 's|<guid[^>]*>||; s|</guid>||') || true; }
        [[ -z "$title" || -z "$url" ]] && continue
        printf '%s\t%s\n' "$url" "$title"
    done <<< "$chunks"
}
