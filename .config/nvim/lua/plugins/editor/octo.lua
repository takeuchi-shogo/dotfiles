return {
  "pwntester/octo.nvim",
  cmd = "Octo",
  keys = {
    -- カスタムキーマップ (<leader>O プレフィックス)
    { "<leader>Oi", "<cmd>Octo issue list<CR>", desc = "Issue list (Octo)" },
    { "<leader>Ois", "<cmd>Octo issue search<CR>", desc = "Issue search (Octo)" },
    { "<leader>Op", "<cmd>Octo pr list<CR>", desc = "PR list (Octo)" },
    { "<leader>Ops", "<cmd>Octo pr search<CR>", desc = "PR search (Octo)" },
    { "<leader>Or", "<cmd>Octo review start<CR>", desc = "Start review (Octo)" },
    { "<leader>Os", "<cmd>Octo search<CR>", desc = "Search (Octo)" },
    -- LazyVim Octo Extra のデフォルトキーマップを無効化
    { "<leader>gi", false },
    { "<leader>gI", false },
    { "<leader>gp", false },
    { "<leader>gP", false },
    { "<leader>gr", false },
    { "<leader>gS", false },
  },
}
