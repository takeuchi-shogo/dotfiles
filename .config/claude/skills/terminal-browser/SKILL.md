---
name: terminal-browser
description: A real browser running inside the terminal. It splits the human's terminal pane automatically, so you can show a website side by side with the conversation, render HTML to visualize something, and drive whatever tab is open — snapshot, click, fill, eval — with the `terminal-browser action` subcommand.
---

> **このセットアップ限定の制約**: herdr 配下では全サブコマンドが
> `could not find this pane in Ghostty` で失敗する。multiplexer 全般ではない —
> v0.4.9 の対応 terminal は tmux / tty7 / wezterm / kitty / cmux / supacode /
> ghostty / vscode で、**herdr だけが未対応**。herdr は pane を特定する env を
> 出しておらず (`HERDR_ENV=1` のみ、`CMUX_PANE` 等は未設定)、`TERM_PROGRAM=ghostty`
> なので ghostty 検出に落ちるが、herdr が張った pty は Ghostty の pane ではないため
> 誰も名乗り出ない。herdr 内では代わりに `agent-browser` (webapp-testing skill) を
> 使う。terminal-browser は herdr を通さない素の Ghostty タブで動く。
> 2026-08-04 (v0.3.3) / 2026-08-10 (v0.4.9) に確認。
>
> **`upgrade` は使えない**: この環境の terminal-browser は nix (home-manager) が
> 配る read-only な store path なので自己更新できない。上げるときは
> `nix/pkgs/terminal-browser.nix` の version/hash を bump して `task nix:switch`。

`terminal-browser open <url>` puts a browser in a terminal pane. On its own it
takes over the current pane. `--split right` (or `down`, `left`, `up`) opens a
new pane beside the human, which is how you show a page next to the
conversation. A path to a local html file works the same as a url, so writing a
page and opening it is a way to show something you built.

`terminal-browser ls` shows the browsers and tabs in this terminal tab, with the
tab ids the other commands take.

`terminal-browser action -- <command>` is an agent-browser compatible CLI for a
tab that is already open. It targets this terminal tab's browser and its active
tab unless you select another one.

## Command reference

```
$ terminal-browser help
Usage: terminal-browser [url] [options]
       terminal-browser <command> [args]

  open      Open the browser in a terminal pane
  ls        List running browsers and their tabs
  setup     Configure installed terminals so terminal-browser works best
  upgrade   Upgrade to the latest release
  new-tab   Open a tab here, and a browser too if there is none
  shutdown  Stop the daemon
  action    Use the open browser through the agent-browser CLI

terminal-browser <command> --help for one command's options
terminal-browser --version prints the installed version
```

```
$ terminal-browser open --help
Usage: terminal-browser open [url] [options]

Opens the browser in the current pane. Pass --split to open it in a new
split pane instead.

The url can be a normal url, a localhost port, or a path to an html file.

Options:
  --split <direction>   Open in a new pane: right, left, down, up
  --size <fraction>     How much of the space the split takes (0.2 to 0.95)

Examples:
  terminal-browser open localhost:3000
  terminal-browser open ./report.html --split right
  terminal-browser open github.com/zenbu-labs --split down --size 0.4
```

```
$ terminal-browser ls --help
Usage: terminal-browser ls [options]

Lists the browsers running in this terminal tab, each with its tabs. The tab
ids it prints are what --tab takes in terminal-browser action.

Options:
  --all               Every browser, not just this terminal tab
  --json              Machine readable, including cdp ports and pane ids
```

```
$ terminal-browser setup --help
Usage: terminal-browser setup

Finds the terminals on this machine and fixes any settings that would keep the
browser from drawing in them. Editors built on vscode ship with terminal images
switched off, so this turns "terminal.integrated.enableImages" on in each one.
```

```
$ terminal-browser upgrade --help
Usage: terminal-browser upgrade

Checks this install's release channel and installs the latest version. Does
nothing when already up to date.
```

```
$ terminal-browser new-tab --help
Usage: terminal-browser new-tab [url] [options]

      Opens a tab in a browser already open. By default, if there is a single browser open
      in the current terminal tab, it will open a tab in that browser. If there are no browsers,
      a new browser will be opened with the specified tab as the initial (if ran from a shell without a TTY, it will open in a split to the right). If there are mulitiple browsers,
      new-tab will error and a --browser <key> is a required argument (<key> can be found by running terminal-browser ls)

      Options:
        --browser <key>     A browser key from terminal-browser ls

      Examples:
        terminal-browser new-tab github.com
        terminal-browser new-tab --browser 90107-1 localhost:3000
```

```
$ terminal-browser shutdown --help
Usage: terminal-browser shutdown

Every browser in a terminal pane shares one browser process as an optimization. To
fully quit terminal-browser operations, you can use this shutdown command. This will
close all open browsers.
```

```
$ terminal-browser action --help
Usage: terminal-browser action [selectors] -- <command>

An agent-browser compatible CLI for the browser you already have open.
Everything after -- is an agent-browser command. With no selectors it targets
the browser in this terminal tab and that browser's active tab.

Selectors:
  --browser <key>     A browser key from terminal-browser ls
  --tab <id>          A tab id from terminal-browser ls
  --target <id>       A CDP target id
  --follow            Bring the tab to the front before running the command

Examples:
  terminal-browser action -- snapshot
  terminal-browser action -- click @e14
  terminal-browser action -- eval "document.title"
  terminal-browser action --browser 90107-1 --tab 2 -- fill @e3 "hello"
```
