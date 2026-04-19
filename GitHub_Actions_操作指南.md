# GitHub Actions 编译操作指南

**仓库地址**: https://github.com/SHAXMN/wxexpoter

---

## ✅ 已完成的步骤

1. ✅ 初始化 Git 仓库
2. ✅ 提交所有代码（386 个文件）
3. ✅ 关联远程仓库
4. ✅ 推送代码到 GitHub
5. ✅ 创建 GitHub Actions 工作流配置
6. ✅ 推送工作流配置

---

## 🚀 下一步：触发编译

### 方法 1: 在 GitHub 网站上手动触发（推荐）

1. **打开仓库页面**
   ```
   https://github.com/SHAXMN/wxexpoter
   ```

2. **进入 Actions 页面**
   - 点击顶部的 "Actions" 标签

3. **选择工作流**
   - 在左侧列表中，点击 "Build WechatExporter"

4. **手动触发编译**
   - 点击右侧的 "Run workflow" 按钮
   - 选择 "Branch: main"
   - 点击绿色的 "Run workflow" 按钮

5. **等待编译完成**
   - 编译过程约需 5-10 分钟
   - 页面会自动刷新显示进度
   - 可以点击工作流查看详细日志

---

## 📥 下载编译产物

### 编译成功后

1. **在 Actions 页面**
   - 点击已完成的工作流运行

2. **下载 Artifacts**
   - 滚动到页面底部
   - 找到 "Artifacts" 部分
   - 点击 "WechatExporter-Enhanced" 下载

3. **解压并使用**
   ```bash
   cd ~/Downloads
   unzip WechatExporter-Enhanced.zip
   unzip WechatExporter.zip
   xattr -cr WechatExporter.app
   open WechatExporter.app
   ```

---

## 🔍 查看编译状态

### 实时查看编译日志

1. 在 Actions 页面点击正在运行的工作流
2. 点击 "build" 作业
3. 展开各个步骤查看详细日志：
   - Checkout code
   - Setup Xcode
   - Build
   - Package app
   - Upload artifact

### 编译成功的标志

- ✅ 所有步骤都显示绿色对勾
- ✅ "Upload artifact" 步骤完成
- ✅ 页面底部显示 "Artifacts" 部分

### 编译失败的处理

如果编译失败：
1. 查看失败步骤的日志
2. 复制错误信息
3. 告诉我错误信息，我会帮您解决

---

## 📊 预期编译时间

| 步骤 | 时间 |
|------|------|
| Checkout code | ~30 秒 |
| Setup Xcode | ~1 分钟 |
| Build | ~3-5 分钟 |
| Package app | ~30 秒 |
| Upload artifact | ~1 分钟 |
| **总计** | **5-10 分钟** |

---

## 🎯 编译完成后的验证

### 1. 检查应用是否可以启动

```bash
cd ~/Downloads
unzip WechatExporter-Enhanced.zip
unzip WechatExporter.zip
xattr -cr WechatExporter.app
open WechatExporter.app
```

### 2. 验证新功能

运行应用后，查看日志输出：

**预期日志**：
```
Finding WeChat accounts...
2 WeChat account(s) found.
Exporting sessions...
Scanning document attachments...          ← 新功能
Found 20520 document attachment(s).       ← 新功能
Exported 20520 document attachment(s).    ← 新功能
Completed in 00:08:32.
```

### 3. 检查导出结果

```bash
# 检查 attachments 目录
ls ~/Documents/WechatExport_Output/attachments/

# 统计附件数量
find ~/Documents/WechatExport_Output/attachments -type f | wc -l

# 打开 HTML 查看链接
open ~/Documents/WechatExport_Output/index.html
```

---

## 🔄 重新编译

如果需要重新编译：

### 方法 1: 手动触发（推荐）

1. 访问 Actions 页面
2. 点击 "Build WechatExporter"
3. 点击 "Run workflow"

### 方法 2: 推送新代码

```bash
# 修改代码后
git add .
git commit -m "Your commit message"
git push

# GitHub Actions 会自动触发编译
```

---

## 📝 故障排除

### 问题 1: 找不到 Actions 标签

**原因**: 仓库可能是私有的，需要确认权限

**解决**:
1. 确认您已登录 GitHub
2. 确认您是仓库的所有者或协作者

### 问题 2: 编译失败 - "No scheme named 'WechatExporter'"

**原因**: Xcode 项目配置问题

**解决**: 告诉我错误日志，我会修复配置

### 问题 3: 下载的文件无法打开

**原因**: macOS 安全限制

**解决**:
```bash
xattr -cr WechatExporter.app
```

### 问题 4: 编译超时

**原因**: GitHub Actions 有时间限制（通常 6 小时）

**解决**: 重新触发编译

---

## 💡 提示

1. **保留编译产物**: Artifacts 默认保留 30 天
2. **多次编译**: 可以随时重新触发编译
3. **查看历史**: 可以查看所有历史编译记录
4. **下载旧版本**: 可以下载之前编译的版本

---

## 📞 需要帮助？

如果遇到任何问题：

1. **截图错误信息**
   - Actions 页面的错误
   - 编译日志中的错误

2. **提供信息**
   - 哪个步骤失败了
   - 完整的错误消息

3. **告诉我**
   - 我会帮您分析和解决

---

## 🎉 成功标志

当您看到以下内容时，说明成功了：

1. ✅ Actions 页面显示绿色对勾
2. ✅ 可以下载 WechatExporter-Enhanced.zip
3. ✅ 应用可以正常启动
4. ✅ 导出时显示 "Scanning document attachments..."
5. ✅ 导出目录中有 attachments/ 文件夹
6. ✅ HTML 中有附件链接

---

**下一步**: 请访问 https://github.com/SHAXMN/wxexpoter/actions 并手动触发编译！
