### Git 學習筆記
1. 將add加入暫存區的文件撤回:

   ```bash
   git rm --cached <filename>
   ```

2. 在修改本地文件後，可以用add來更新，而撤銷更新的命令為：

   ```bash
   git checkout -- <filename>
   ```

3. 查看提交記錄

   ```bash
   git log
   ```

   如果只想查看部分關鍵信息，則可以

   ```bash
   git log --pretty=oneline
   或者
   git logh --oneline
   或者
   git reflog
   這個顯示了到某一個版本需要移動幾步
   ```

4. 版本回退，主要有三種方式：

   1. 索引。通過```git reflog```命令可以查看提交記錄，然後通過

      ```bash
      git reset --hard number
      ```

      number表示索引號，這個在提交記錄中可以找到。

   2. ^符號進行回退。

      ```bash
      git reset --hard HEAD^
      ```

      回退的版本數量與^符號的數量有關

   3. ~符號進行回退

      ```bash
      git reset --hrad HEAD~n
      ```

      n表示需要回退的版本數量
