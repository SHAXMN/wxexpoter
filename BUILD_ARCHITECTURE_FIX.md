# 构建架构修复说明

## 问题分析

### 1. 架构不匹配
- **本地环境**: Intel Mac (x86_64)
- **GitHub Actions**: 默认使用 Apple Silicon (arm64)
- **结果**: 构建的 app 无法在本地 Intel Mac 上运行

### 2. 库版本号问题
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

## 解决方案

### 方案 1: 使用 Intel Runner（推荐）

创建了新的 workflow 文件 `.github/workflows/build-intel.yml`：

**关键改动**：
1. **使用 macOS 13 runner**: `runs-on: macos-13`
   - macOS 13 runner 使用 Intel x86_64 架构
   - macOS 14+ runner 使用 Apple Silicon arm64 架构

2. **复制库文件而非符号链接**:
   ```bash
   cp $LIBIMOBILEDEVICE_PREFIX/lib/libimobiledevice-1.0.dylib \
      releases/windows-libs/x64/rel/bin/libimobiledevice-1.0.6.dylib
   ```
   - 直接复制实际的 dylib 文件
   - 使用项目期望的旧版本文件名

3. **明确指定 x86_64 架构**:
   ```bash
   ARCHS=x86_64
   ONLY_ACTIVE_ARCH=YES
   ```

### 方案 2: 修改项目文件（长期方案）

如果想彻底解决版本号问题，需要修改 Xcode 项目文件：

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

## 使用说明

### 触发构建

1. **自动触发**: 推送到 main 分支或创建 PR
2. **手动触发**: 
   - 进入 GitHub Actions 页面
   - 选择 "Build WechatExporter (Intel x86_64)" workflow
   - 点击 "Run workflow"

### 下载构建产物

1. 进入 Actions 页面
2. 选择成功的 workflow run
3. 下载 "WechatExporter-Intel-x86_64" artifact
4. 解压 `WechatExporter-Intel.zip`
5. 将 `WechatExporter.app` 拖到 Applications 文件夹

### 验证架构

```bash
# 检查 app 的架构
file WechatExporter.app/Contents/MacOS/WechatExporter

# 应该显示: Mach-O 64-bit executable x86_64
```

## 两个 Workflow 的区别

| 特性 | build.yml (原版) | build-intel.yml (新版) |
|------|------------------|------------------------|
| Runner | macos-latest (arm64) | macos-13 (x86_64) |
| 目标架构 | arm64 | x86_64 |
| 适用设备 | Apple Silicon Mac | Intel Mac |
| Artifact 名称 | WechatExporter-Enhanced | WechatExporter-Intel-x86_64 |

## 常见问题

### Q: 为什么不构建 Universal Binary？
A: Universal Binary 需要同时链接 arm64 和 x86_64 的依赖库，但 Homebrew 在不同架构上安装的库是单架构的。要构建 Universal Binary 需要：
- 分别在 arm64 和 x86_64 环境中构建
- 使用 `lipo` 工具合并两个版本
- 更复杂的 CI 配置

### Q: 构建失败怎么办？
A: 检查以下几点：
1. 确认使用的是 `macos-13` runner（Intel）
2. 检查 Homebrew 是否成功安装所有依赖
3. 查看 "Diagnose dependencies" 步骤的输出
4. 确认 `releases/windows-libs/x64/rel/bin/` 目录中的库文件架构正确

### Q: 本地如何测试？
A: 在 Intel Mac 上：
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
sudo cp interface/*.h /usr/local/include/silk/
sudo cp src/*.h /usr/local/include/silk/
sudo cp libSKP_SILK_SDK.a /usr/local/lib/

# 创建库文件
cd ~/Documents/Quant/WechatExporter
mkdir -p releases/windows-libs/x64/rel/bin
cp /usr/local/opt/lame/lib/libmp3lame.dylib releases/windows-libs/x64/rel/bin/libmp3lame.0.dylib
cp /usr/local/opt/libimobiledevice/lib/libimobiledevice-1.0.dylib releases/windows-libs/x64/rel/bin/libimobiledevice-1.0.6.dylib
cp /usr/local/opt/libplist/lib/libplist-2.0.dylib releases/windows-libs/x64/rel/bin/libplist-2.0.3.dylib
cp /usr/local/opt/libusbmuxd/lib/libusbmuxd-2.0.dylib releases/windows-libs/x64/rel/bin/libusbmuxd-2.0.6.dylib
cp /usr/local/opt/libimobiledevice-glue/lib/libimobiledevice-glue-1.0.dylib releases/windows-libs/x64/rel/bin/libimobiledevice-glue-1.0.0.dylib

# 使用 Xcode 构建
xcodebuild clean build \
  -project WechatExporter.xcodeproj \
  -scheme WechatExporter \
  -configuration Release
```

## 下一步

1. **测试新 workflow**: 推送代码触发构建，验证生成的 app 能在 Intel Mac 上运行
2. **考虑长期方案**: 如果确认可行，可以考虑修改项目文件去掉版本号
3. **添加 Universal Binary 支持**: 如果需要同时支持两种架构

## 参考

- [GitHub Actions - macOS runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-runners-and-hardware-resources)
- [Xcode Build Settings Reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Homebrew on Apple Silicon](https://docs.brew.sh/Installation#macos-requirements)
