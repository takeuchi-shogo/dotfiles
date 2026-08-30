-- VS Code 風の左サイドバー。表示/非表示は LazyVim extra の <leader>e（toggle）。
local function should_show_tree()
  if vim.g.vscode then
    return false
  end
  if vim.tbl_contains(vim.v.argv, "-") then
    return false
  end
  for _, arg in ipairs(vim.fn.argv()) do
    arg = tostring(arg)
    if arg:match("COMMIT_EDITMSG") or arg:match("git%-rebase%-todo") or arg:match("MERGE_MSG") then
      return false
    end
  end
  return true
end

return {
  "nvim-neo-tree/neo-tree.nvim",
  opts = {
    close_if_last_window = true,
  },
  init = function()
    vim.api.nvim_create_autocmd("VimEnter", {
      group = vim.api.nvim_create_augroup("neotree_auto_show", { clear = true }),
      desc = "Show Neo-tree sidebar on startup without stealing focus",
      once = true,
      callback = function()
        if not should_show_tree() then
          return
        end
        vim.schedule(function()
          require("neo-tree.command").execute({
            action = "show",
            source = "filesystem",
            dir = LazyVim.root(),
          })
        end)
      end,
    })
  end,
}
