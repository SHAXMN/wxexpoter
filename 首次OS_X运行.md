# WechatExporter 在 macOS 下的运行指引

**日期**: 2026-04-18  
**系统**: macOS 12.7.6 (Monterey)  
**当前状态**: 已下载源码到 `/Users/HuBin/Documents/Quant/WechatExporter`

---

## ⚠️ 重要发现

您当前只有源码，没有编译好的可执行文件。而且系统只安装了 Command Line Tools，没有完整的 Xcode，**无法直接编译**。

**推荐方案**：下载预编译版本（无需编译，直接运行）

---

## 📋 前提条件

1. ✅ 已通过 iTunes 备份 iPhone（**备份时不要设置密码**）
2. ✅ 备份位置：`~/Library/Application Support/MobileSync/Backup/`
3. ✅ 您的备份 ID：`00008140-000139E62247001C`

---

## 🚀 方案一：下载预编译版本（强烈推荐）

**优点**：
- ✅ 无需安装 Xcode（节省 10+ GB 空间）
- ✅ 无需编译依赖库
- ✅ 5 分钟内即可开始使用

### 步骤 1: 下载预编译版本

```bash
# 创建临时目录
mkdir -p ~/Downloads/WechatExporter_Prebuilt
cd ~/Downloads/WechatExporter_Prebuilt

# 下载预编译版本
curl -L -O https://github.com/BlueMatthew/WechatExporter/releases/download/v1.8.0.10/v1.8.0.10_x64_macos.zip
```

### 步骤 2: 解压

```bash
unzip v1.8.0.10_x64_macos.zip
```

### 步骤 3: 移除 macOS 安全限制

macOS 会阻止未签名的应用运行，需要移除扩展属性：

```bash
xattr -cr WechatExporter.app
```

### 步骤 4: 启动应用

```bash
open WechatExporter.app
```

**如果仍然无法打开**，尝试：
1. 在 Finder 中找到 `WechatExporter.app`
2. 按住 Control 键点击（或右键点击）
3. 选择"打开"
4. 在弹出的对话框中点击"打开"

---

## 🛠️ 方案二：从源码编译（需要安装 Xcode）

**当前状态**：
- ❌ 未安装完整的 Xcode（只有 Command Line Tools）
- ✅ 已有源码：`/Users/HuBin/Documents/Quant/WechatExporter`

**如果要编译，需要先安装 Xcode**：

### 安装 Xcode

1. **从 App Store 安装**（推荐）
   - 打开 App Store
   - 搜索 "Xcode"
   - 点击"获取"或"安装"
   - ⚠️ 下载大小约 12 GB，安装后占用约 40 GB

2. **或从 Apple Developer 下载**
   - 访问：https://developer.apple.com/download/
   - 下载适合 macOS 12.7.6 的 Xcode 版本
   - 推荐：Xcode 14.2（最后支持 macOS 12 的版本）

### 编译步骤

安装 Xcode 后：

```bash
cd /Users/HuBin/Documents/Quant/WechatExporter

# 使用 Xcode 打开项目
open WechatExporter.xcodeproj
```

在 Xcode 中：
1. 选择菜单 Product → Build（或按 ⌘B）
2. 等待编译完成（首次编译可能需要 5-10 分钟）
3. 选择菜单 Product → Run（或按 ⌘R）

**注意**：编译需要以下依赖库（部分需要手动编译）：
- ✅ libxml2（Xcode 自带）
- ✅ libcurl（Xcode 自带）
- ✅ libsqlite3（Xcode 自带）
- ❌ libprotobuf（需要自行编译）
- ❌ libjsoncpp（需要自行编译）
- ❌ lame（需要自行编译）
- ❌ silk（需要自行编译）
- ❌ libplist（需要自行编译）

**由于依赖库编译复杂，强烈建议使用方案一（预编译版本）。**

---

## 📱 使用 WechatExporter

### 界面操作流程

1. **选择备份**
   - 程序启动后，点击"选择备份"或"浏览"按钮
   - 导航到：`~/Library/Application Support/MobileSync/Backup/00008140-000139E62247001C`
   - 或者程序可能自动检测到备份

2. **选择微信用户**
   - 程序会列出备份中的所有微信账号
   - 选择您要导出的账号（可能显示为手机号或昵称）

3. **选择会话**
   - 勾选要导出的聊天会话
   - 可以选择"全部"导出所有会话
   - 或者只选择特定的联系人/群组

4. **选择输出目录**
   - 点击"选择输出目录"
   - 建议选择：`~/Documents/WechatExport_Output`

5. **开始导出**
   - 点击"导出"或"开始"按钮
   - 等待进度条完成
   - 导出过程可能需要几分钟到几十分钟，取决于消息数量

6. **查看结果**
   ```bash
   open ~/Documents/WechatExport_Output/index.html
   ```

---

## ⚙️ 高级选项

### 导出格式

WechatExporter 支持三种导出格式：
- **HTML**（默认）：网页格式，可以在浏览器中查看
- **Text**：纯文本格式
- **PDF**：通过 Chrome/Edge 浏览器转换

### 加载方式

在菜单"选项"中可以设置：
- 打开时一次性加载完成（默认）
- 打开时异步加载
- 页面滑动到底部时加载更多

### 增量导出

在菜单"选项"中启用增量导出：
- 仅导出上次导出后的新消息
- 可以定期备份并导出，然后删除手机上的聊天记录
- 下次导出时会自动合并到同一个文件中

---

## ❓ 常见问题

### Q1: 提示"无法打开，因为无法验证开发者"

**解决方法**：
```bash
xattr -cr WechatExporter.app
```

或者：
1. 系统偏好设置 → 安全性与隐私
2. 点击"仍要打开"

### Q2: 找不到 iTunes 备份

**检查备份位置**：
```bash
ls -la ~/Library/Application\ Support/MobileSync/Backup/
```

**确认备份是否加密**：
- iTunes 备份时**不要设置密码**
- 加密的备份无法直接读取

### Q3: 导出的聊天记录不完整

**可能原因**：
- iTunes 备份不完整
- 微信版本过旧或过新
- 使用了 1.8.0.7 之前的版本（有 bug）

**解决方法**：
- 使用最新版本（1.8.0.10）
- 重新进行 iTunes 备份
- 如果已经导出过，可以使用补丁程序修复

### Q4: 导出速度很慢

**正常情况**：
- 大量消息（几万条）需要较长时间
- 包含大量图片/视频会更慢

**优化建议**：
- 只导出需要的会话
- 关闭其他占用 CPU 的程序

---

## 📊 已测试的版本组合

WechatExporter 已在以下环境测试通过：

| macOS 版本 | iTunes 版本 | iOS 版本 | 微信版本 |
|-----------|------------|---------|---------|
| Catalina | Embedded | 15.0 | 8.0.9 |
| 11.6 | Embedded | 15.0 | 8.0.9 |
| Monterey | Embedded | 15.0 | 8.0.9 |

**您的环境**：
- macOS: 12.7.6 (Monterey)
- iOS: 15.0
- 微信: 8.0.9
- ✅ 应该可以正常工作

---

## 🎯 快速开始（一键命令）

```bash
# 下载、解压、启动（一键执行）
mkdir -p ~/Downloads/WechatExporter_Prebuilt && \
cd ~/Downloads/WechatExporter_Prebuilt && \
curl -L -O https://github.com/BlueMatthew/WechatExporter/releases/download/v1.8.0.10/v1.8.0.10_x64_macos.zip && \
unzip -q v1.8.0.10_x64_macos.zip && \
xattr -cr WechatExporter.app && \
open WechatExporter.app

echo "✅ WechatExporter 已启动！"
echo "📂 iTunes 备份位置: ~/Library/Application Support/MobileSync/Backup/00008140-000139E62247001C"
echo "📁 建议输出目录: ~/Documents/WechatExport_Output"
```

---

## 📝 重要提示

1. **不需要密钥**：iTunes 未加密备份中的微信数据库已经是解密的，WechatExporter 可以直接读取
2. **备份不要加密**：如果 iTunes 备份时设置了密码，需要重新进行未加密备份
3. **保留备份**：导出完成后，建议保留 iTunes 备份，以便将来需要时重新导出
4. **隐私保护**：导出的聊天记录包含完整的消息内容，请妥善保管

---

## 🔗 相关链接

- GitHub 项目：https://github.com/BlueMatthew/WechatExporter
- 最新版本：https://github.com/BlueMatthew/WechatExporter/releases
- 在线演示：https://src.wakin.org/github/wxexp/demo/

---

**祝您导出顺利！** 🎉
