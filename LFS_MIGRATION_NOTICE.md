# LFS Migration Notice

更新日期：2025-10-29

我們已將檔案 `twdtm_asterV2_30m.tif` 遷移到 Git LFS，並對 `main` 分支的歷史進行改寫（以移除超大檔案的普通 Git 物件）。

如果你有此 repository 的本地 clone，請務必重設你的本地分支以避免衝突。建議步驟：

```bash
git fetch origin
git checkout main
git reset --hard origin/main
git lfs install
git lfs pull
```

說明：
- 我們使用 `git lfs migrate import --include="twdtm_asterV2_30m.tif"` 將該檔案轉為 LFS 物件，並用 `git push --force-with-lease` 推送改寫後的歷史。
- 如果你有其他 branch 基於舊的 commit，請先備份並以 rebase 或重建方式處理，避免資料遺失。
- GitHub 的 Git LFS 會有儲存與頻寬配額，請在需要大量或頻繁上傳大檔時評估是否使用外部儲存（例如 S3、GCS，或 GitHub Releases）。

如需協助（例如為團隊撰寫通知或協助其他協作者重設本地環境），請告訴我，我可以幫忙產生通知文字或在 repo 中新增更多說明檔案。
