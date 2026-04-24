# Phase 0+A fixture: unmanaged sibling

このファイルは `claude-like/` ディレクトリ全体を `mkOutOfStoreSymlink` で symlink した場合に、
意図せず管理対象に含まれていないか (or 含まれているか) を観察する。
本番の Phase B2 では `.config/claude/` 配下の unmanaged な runtime state との共存を設計する必要があり、
その sneak preview として機能させる。
