# ディレクトリ移動後に自動でls（対話シェルのみ。非対話シェルでの出力汚染を防ぐ）
chpwd() {
  [[ -o interactive ]] && ls -la
}
