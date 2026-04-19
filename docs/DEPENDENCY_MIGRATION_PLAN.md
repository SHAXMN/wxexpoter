# 依赖迁移计划：完全使用仓库内的库

## 目标

将项目从"混用 Homebrew 头文件 + 仓库内旧二进制"模式迁移到"完全使用仓库内的库"模式，消除 CI 环境漂移风险。

## 当前问题

1. **头文件与二进制版本不匹配**：编译时使用 Homebrew 最新头文件，链接时使用仓库内旧版本 dylib
2. **环境漂移**：Homebrew 包每次更新可能引入 API 变化
3. **架构不匹配风险**：仓库内的 dylib 可能不包含 arm64 架构

## 实施步骤

### 阶段 1：清点和验证现有库（1-2 小时）

#### 1.1 检查仓库内现有的库文件

```bash
# 查找所有 dylib 文件
find . -name "*.dylib" -o -name "*.a"

# 检查架构
file releases/windows-libs/x64/rel/bin/*.dylib
lipo -info releases/windows-libs/x64/rel/bin/*.dylib
```

#### 1.2 列出项目依赖的所有库

根据 `WechatExporter.xcodeproj/project.pbxproj`，项目需要：

- `libimobiledevice-1.0.6.dylib`
- `libplist-2.0.3.dylib`
- `libusbmuxd-2.0.6.dylib`
- `libimobiledevice-glue-1.0.0.dylib`
- `libcrypto.1.1.dylib`
- `libssl.1.1.dylib`
- `libmp3lame.0.dylib`
- `libSKP_SILK_SDK.a`
- `libjsoncpp.dylib`
- `libprotobuf.dylib`
- `libabsl_*.dylib` (多个 abseil 库)
- `libopencore-amrnb.dylib`
- `libopencore-amrwb.dylib`

#### 1.3 验证缺失的库

```bash
# 检查哪些库不在仓库中
for lib in libimobiledevice libplist libusbmuxd libimobiledevice-glue \
           libcrypto libssl libmp3lame libjsoncpp libprotobuf \
           libopencore-amrnb libopencore-amrwb; do
  find . -name "${lib}*.dylib" -o -name "${lib}*.a" || echo "Missing: $lib"
done
```

### 阶段 2：构建 arm64 兼容的库（2-4 小时）

#### 2.1 创建库构建脚本

创建 `scripts/build-dependencies.sh`：

```bash
#!/bin/bash
set -e

# 目标架构
ARCHS="arm64 x86_64"
MACOSX_DEPLOYMENT_TARGET="10.13"

# 输出目录
OUTPUT_DIR="$(pwd)/vendor/libs"
INCLUDE_DIR="$(pwd)/vendor/include"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$INCLUDE_DIR"

# 构建每个依赖库
# 1. libplist
# 2. libusbmuxd
# 3. libimobiledevice-glue
# 4. libimobiledevice
# 5. openssl (1.1.x)
# 6. lame
# 7. opencore-amr
# 8. jsoncpp
# 9. protobuf
# 10. abseil

# 每个库的构建步骤：
# - 下载指定版本源码
# - 配置为 universal binary (arm64 + x86_64)
# - 编译
# - 安装到 vendor/ 目录
```

#### 2.2 固定依赖版本

创建 `vendor/VERSIONS.txt`：

```
libplist=2.2.0
libusbmuxd=2.0.2
libimobiledevice-glue=1.0.0
libimobiledevice=1.3.0
openssl=1.1.1w
lame=3.100
opencore-amr=0.1.6
jsoncpp=1.9.5
protobuf=21.12
abseil=20230125.3
```

### 阶段 3：更新项目配置（1 小时）

#### 3.1 修改 Xcode 项目设置

在 `WechatExporter.xcodeproj/project.pbxproj` 中：

1. 移除所有 `/opt/homebrew` 和 `/usr/local` 路径
2. 添加 `$(PROJECT_DIR)/vendor/include` 到 `HEADER_SEARCH_PATHS`
3. 添加 `$(PROJECT_DIR)/vendor/libs` 到 `LIBRARY_SEARCH_PATHS`
4. 更新 Framework Search Paths

#### 3.2 更新链接的库文件引用

将所有库引用从：
```
/opt/homebrew/opt/libplist/lib/libplist-2.0.dylib
```

改为：
```
$(PROJECT_DIR)/vendor/libs/libplist-2.0.dylib
```

### 阶段 4：更新 CI 配置（30 分钟）

#### 4.1 简化 GitHub Actions workflow

修改 `.github/workflows/build.yml`：

```yaml
- name: Install dependencies
  run: |
    # 只需要构建 silk（因为它不在 vendor/ 中）
    cd /tmp
    git clone https://github.com/collects/silk.git
    cd silk
    sed -i '' 's/-enable-threads//g' Makefile
    make lib 2>&1 | grep -v "warning:" || true
    
    # 安装到项目 vendor 目录
    mkdir -p vendor/include/silk
    mkdir -p vendor/libs
    cp interface/*.h vendor/include/silk/
    cp src/*.h vendor/include/silk/
    cp libSKP_SILK_SDK.a vendor/libs/

- name: Build
  run: |
    # 不再需要 brew --prefix，直接使用 vendor/
    xcodebuild clean build \
      -project WechatExporter.xcodeproj \
      -scheme WechatExporter \
      -configuration Release \
      -derivedDataPath ./build
```

#### 4.2 移除 Homebrew 依赖

删除所有 `brew install` 命令（除了可能需要的构建工具）。

### 阶段 5：验证和测试（1-2 小时）

#### 5.1 本地验证

```bash
# 清理所有 Homebrew 库（临时测试）
brew uninstall libplist libimobiledevice jsoncpp protobuf abseil opencore-amr lame

# 尝试构建
xcodebuild clean build -project WechatExporter.xcodeproj -scheme WechatExporter

# 验证链接的库都来自 vendor/
otool -L build/Build/Products/Release/WechatExporter.app/Contents/MacOS/WechatExporter
```

#### 5.2 CI 验证

推送到 GitHub，观察 Actions 构建结果。

#### 5.3 功能测试

- 启动应用
- 测试 iTunes 备份解析
- 测试微信数据导出
- 测试音频转换（silk, mp3）

## 风险和缓解措施

### 风险 1：构建脚本复杂度高

**缓解**：
- 使用 vcpkg 或 conan 等包管理器简化构建
- 或者直接从 Homebrew 复制已编译的 universal binary

### 风险 2：库文件体积大

**缓解**：
- 使用 Git LFS 存储二进制文件
- 或者在 CI 中动态下载预编译库

### 风险 3：OpenSSL 1.1.x 已 EOL

**缓解**：
- 考虑升级到 OpenSSL 3.x
- 或者使用系统自带的 Security.framework

## 替代方案：使用预编译库

如果从源码构建太复杂，可以：

1. 在本地用 Homebrew 安装所有依赖
2. 复制编译好的 dylib 到 `vendor/libs/`
3. 复制头文件到 `vendor/include/`
4. 提交到仓库

```bash
# 示例脚本
for pkg in libplist libimobiledevice jsoncpp protobuf abseil opencore-amr lame; do
  PREFIX=$(brew --prefix $pkg)
  cp -r $PREFIX/lib/*.dylib vendor/libs/ 2>/dev/null || true
  cp -r $PREFIX/lib/*.a vendor/libs/ 2>/dev/null || true
  cp -r $PREFIX/include/* vendor/include/ 2>/dev/null || true
done
```

## 时间估算

- **快速方案**（使用预编译库）：2-3 小时
- **完整方案**（从源码构建）：8-12 小时

## 下一步行动

1. ✅ 应用立即修复（诊断步骤）
2. ⬜ 决定使用快速方案还是完整方案
3. ⬜ 执行阶段 1：清点现有库
4. ⬜ 执行阶段 2 或替代方案：获取 arm64 兼容库
5. ⬜ 执行阶段 3：更新项目配置
6. ⬜ 执行阶段 4：更新 CI
7. ⬜ 执行阶段 5：验证

## 参考资料

- [libimobiledevice GitHub](https://github.com/libimobiledevice/libimobiledevice)
- [Homebrew Formula](https://formulae.brew.sh/)
- [Xcode Build Settings Reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
