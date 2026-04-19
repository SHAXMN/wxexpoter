# 构建架构修复说明

## 问题分析

### 1. 架构不匹配
- **本地环境**: Intel Mac (x86_64)
- **GitHub Actions**: 默认使用 Apple Silicon (arm64)
- **结果**: 构建的 app 无法在本地 Intel Mac 上运行

### 2. macOS 13 Runner 即将退役
- GitHub 已宣布 `macos-13` (Intel) runner 将在 2025 年 12 月完全下线
- 当前 (2026 年 4 月) Intel runner 数量极少，排队时间长（5-30 分钟）
- 不适合作为长期解决方案

### 3. 库版本号问题
项目文件中硬编码了带版本号的库名：
- `libimobiledevice-1.0.6.dylib`
- `libplist-2.0.3.dylib`
- `libusbmuxd-2.0.6.dylib`
- `libimobiledevice-glue-1.0.0.dylib`

但 Homebrew 2026 年版本中，这些库的实际名称已变为：
- `libimobiledevice-1.0.dylib`
- `libplist-2.0.dylib`
- `libusbmuxd-2.0.dylib`
- `libimobiledevice-glue-1.0.dylib`

## 解决方案：Universal Binary（推荐）

创建了新的 workflow 文件 `.github/workflows/build-intel.yml`，构建 **Universal Binary**：

### 为什么选择 Universal Binary？

✅ **无需等待稀缺的 Intel runner**（macos-13 即将退役）  
✅ **一个 app 同时支持 Intel 和 Apple Silicon**  
✅ **构建速度更快**（使用 macos-latest 的 arm64 runner）  
✅ **未来兼容性更好**  

### 关键配置

1. **使用最新的 macOS runner**:
   ```yaml
   runs-on: macos-latest  # arm64 架构，但可以交叉编译
   ```

2. **构建 Universal Binary**:
   ```bash
   ARCHS="arm64 x86_64"
   ONLY_ACTIVE_ARCH=NO
   ```

3. **复制库文件**:
   ```bash
   cp $LIBIMOBILEDEVICE_PREFIX/lib/libimobiledevice-1.0.dylib \
      releases/windows-libs/x64/rel/bin/libimobiledevice-1.0.6.dylib
   ```

### 验证 Universal Binary

构建完成后，workflow 会自动验证：
```bash
lipo -info WechatExporter.app/Contents/MacOS/WechatExporter
# 输出: Architectures in the fat file: arm64 x86_64
```

## 两个 Workflow 的区别

| 特性 | build.yml (原版) | build-intel.yml (Universal) |
|------|------------------|------------------------------|
| Runner | macos-latest (arm64) | macos-latest (arm64) |
| 目标架构 | arm64 | arm64 + x86_64 (Universal) |
| 适用设备 | Apple Silicon Mac | **Intel Mac + Apple Silicon Mac** |
| 构建速度 | 快 | 快 |
| Artifact 名称 | WechatExporter-Enhanced | WechatExporter-Universal |
| 推荐使用 | Apple Silicon 用户 | **所有用户（推荐）** |

## 使用说明

### 触发构建

1. **自动触发**: 推送到 main 分支或创建 PR
2. **手动触发**: 
   - 进入 GitHub Actions 页面
   - 选择 "Build WechatExporter (Universal Binary)" workflow
   - 点击 "Run workflow"

### 下载构建产物

1. 进入 Actions 页面
2. 选择成功的 workflow run
3. 下载 "WechatExporter-Universal" artifact
4. 解压 `WechatExporter-Universal.zip`
5. 将 `WechatExporter.app` 拖到 Applications 文件夹

### 验证架构

```bash
# 检查 app 的架构
lipo -info WechatExporter.app/Contents/MacOS/WechatExporter

# 应该显示: Architectures in the fat file: WechatExporter.app/Contents/MacOS/WechatExporter are: x86_64 arm64
```

这意味着：
- ✅ 可以在 Intel Mac (x86_64) 上运行
- ✅ 可以在 Apple Silicon Mac (arm64) 上运行

## 常见问题

### Q: Universal Binary 会增加文件大小吗？
A: 是的，大约会增加 2 倍大小（因为包含两个架构的代码）。但这是值得的，因为：
- 一个 app 适用所有 Mac
- 无需维护两个版本
- 用户体验更好

### Q: 为什么不直接使用 macos-13 构建 x86_64？
A: 因为：
- macos-13 runner 即将完全退役（2025 年 12 月）
- 当前排队时间很长（5-30 分钟）
- Universal Binary 是 Apple 推荐的最佳实践

### Q: 构建失败怎么办？
A: 检查以下几点：
1. 确认使用的是 `macos-latest` runner
2. 检查 Homebrew 是否成功安装所有依赖
3. 查看 "Diagnose dependencies" 步骤的输出
4. 确认 `releases/windows-libs/x64/rel/bin/` 目录中的库文件存在

### Q: 本地如何测试？
A: 在任何 Mac 上（Intel 或 Apple Silicon）：
```bash
# 安装依赖
brew install jsoncpp protobuf abseil libplist opencore-amr lame \
             libimobiledevice libimobiledevice-glue libusbmuxd

# 编译 silk
cd /tmp
git clone https://github.com/collects/silk.git
cd silk
sed -i '' 's/-enable-threads//g' Makefile
make lib
sudo mkdir -p /usr/local/include/silk /usr/local/lib
sudo cp interface/*.h /usr/local/include/silk/
sudo cp src/*.h /usr/local/include/silk/
sudo cp libSKP_SILK_SDK.a /usr/local/lib/

# 创建库文件
cd ~/Documents/Quant/WechatExporter
mkdir -p releases/windows-libs/x64/rel/bin

# 获取 Homebrew 前缀（Apple Silicon 是 /opt/homebrew，Intel 是 /usr/local）
BREW_PREFIX=$(brew --prefix)

cp $BREW_PREFIX/opt/lame/lib/libmp3lame.dylib releases/windows-libs/x64/rel/bin/libmp3lame.0.dylib
cp $BREW_PREFIX/opt/libimobiledevice/lib/libimobiledevice-1.0.dylib releases/windows-libs/x64/rel/bin/libimobiledevice-1.0.6.dylib
cp $BREW_PREFIX/opt/libplist/lib/libplist-2.0.dylib releases/windows-libs/x64/rel/bin/libplist-2.0.3.dylib
cp $BREW_PREFIX/opt/libusbmuxd/lib/libusbmuxd-2.0.dylib releases/windows-libs/x64/rel/bin/libusbmuxd-2.0.6.dylib
cp $BREW_PREFIX/opt/libimobiledevice-glue/lib/libimobiledevice-glue-1.0.dylib releases/windows-libs/x64/rel/bin/libimobiledevice-glue-1.0.0.dylib

# 使用 Xcode 构建 Universal Binary
xcodebuild clean build \
  -project WechatExporter.xcodeproj \
  -scheme WechatExporter \
  -configuration Release \
  ARCHS="arm64 x86_64" \
  ONLY_ACTIVE_ARCH=NO

# 验证架构
lipo -info build/Build/Products/Release/WechatExporter.app/Contents/MacOS/WechatExporter
```

## 长期优化方案（可选）

如果想彻底解决版本号问题，可以修改 Xcode 项目文件：

1. 编辑 `WechatExporter.xcodeproj/project.pbxproj`
2. 搜索并替换：
   - `libimobiledevice-1.0.6.dylib` → `libimobiledevice-1.0.dylib`
   - `libplist-2.0.3.dylib` → `libplist-2.0.dylib`
   - `libusbmuxd-2.0.6.dylib` → `libusbmuxd-2.0.dylib`
   - `libimobiledevice-glue-1.0.0.dylib` → `libimobiledevice-glue-1.0.dylib`

3. 同时修改 `WechatExporterCmd.xcodeproj/project.pbxproj`

**优点**: 
- 不需要在 CI 中创建兼容性文件
- 直接使用 Homebrew 的标准库名

**缺点**: 
- 需要修改多个地方
- 可能影响其他开发者的环境

## 参考

- [GitHub Actions - macOS runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)
- [Xcode Build Settings Reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Building a Universal macOS Binary](https://developer.apple.com/documentation/apple-silicon/building-a-universal-macos-binary)
- [Homebrew on Apple Silicon](https://docs.brew.sh/Installation#macos-requirements)
