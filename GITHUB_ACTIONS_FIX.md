# GitHub Actions 构建修复说明

## 问题诊断

### PR #48 错误
```
cp: /opt/homebrew/opt/lame/lib/libmp3lame.dylib: No such file or directory
```

### PR #11 错误
```
ld: library 'crypto' not found
clang++: error: linker command failed with exit code 1
```

## 根本原因

虽然 workflow 配置中已经安装了 `openssl@3` 并设置了 `LIBRARY_SEARCH_PATHS`，但在实际的链接阶段，OpenSSL 的库路径没有被正确传递给链接器。

从构建日志可以看到：
- 编译阶段的头文件路径包含了所有依赖
- 但链接命令中缺少 OpenSSL 的 `-L` 路径
- 导致链接器找不到 `libcrypto` 和 `libssl`

## 解决方案

### 修改 1: `.github/workflows/build.yml`

在 xcodebuild 命令中添加 `OTHER_LDFLAGS` 参数，显式指定 OpenSSL 库路径：

```yaml
xcodebuild clean build \
  -project WechatExporter.xcodeproj \
  -scheme WechatExporter \
  -configuration Release \
  -derivedDataPath ./build \
  ARCHS=arm64 \
  ONLY_ACTIVE_ARCH=YES \
  "HEADER_SEARCH_PATHS=..." \
  "LIBRARY_SEARCH_PATHS=..." \
  "OTHER_LDFLAGS=-L$OPENSSL_PREFIX/lib"  # 新增此行
```

同时添加了调试输出，打印实际使用的路径。

### 修改 2: `.github/workflows/build-intel.yml`

1. **添加 openssl@3 依赖**：
   ```yaml
   brew install ... openssl@3
   ```

2. **添加 OpenSSL 路径到变量**：
   ```bash
   OPENSSL_PREFIX=$(brew --prefix openssl@3)
   ```

3. **更新头文件和库搜索路径**：
   ```bash
   HEADER_PATHS="... $OPENSSL_PREFIX/include ..."
   LIBRARY_PATHS="... $OPENSSL_PREFIX/lib ..."
   ```

4. **添加 OTHER_LDFLAGS**：
   ```yaml
   OTHER_LDFLAGS="-L$OPENSSL_PREFIX/lib"
   ```

5. **添加诊断输出**：
   显示 OpenSSL 库的位置和版本信息。

## 技术细节

### 为什么需要 OTHER_LDFLAGS？

Xcode 的 `LIBRARY_SEARCH_PATHS` 设置有时不会完全覆盖项目文件中的配置。`OTHER_LDFLAGS` 直接将参数传递给链接器，确保路径被正确使用。

### OpenSSL 3 的特殊性

- OpenSSL 3 在 Homebrew 中是 "keg-only"，不会自动链接到系统路径
- 必须显式指定其路径：`/opt/homebrew/opt/openssl@3` (arm64) 或 `/usr/local/opt/openssl@3` (x86_64)
- 项目代码中使用了 `-lcrypto -lssl`，需要确保链接器能找到这些库

### 架构说明

- **GitHub Actions runner**: arm64 (Apple Silicon)
- **本地开发环境**: x86_64 (Intel)
- **构建目标**: arm64 (可在 Intel Mac 上通过 Rosetta 2 运行)
- **Homebrew 路径**:
  - arm64: `/opt/homebrew`
  - x86_64: `/usr/local`

## 验证步骤

修改后，构建过程应该：

1. ✅ 成功安装所有依赖（包括 openssl@3）
2. ✅ 正确复制所需的 dylib 文件
3. ✅ 编译所有源文件（可能有警告，但不应有错误）
4. ✅ 成功链接，找到 libcrypto 和 libssl
5. ✅ 生成可执行的 WechatExporter.app

## 预期输出

构建日志中应该看到：

```
Header paths: ... /opt/homebrew/opt/openssl@3/include ...
Library paths: ... /opt/homebrew/opt/openssl@3/lib ...

=== Linked libraries ===
/opt/homebrew/opt/openssl@3/lib/libcrypto.3.dylib
/opt/homebrew/opt/openssl@3/lib/libssl.3.dylib
...
```

## 后续建议

如果此修复成功，建议：

1. 在本地 x86_64 Mac 上测试构建
2. 验证生成的 app 在 Intel Mac 上通过 Rosetta 2 正常运行
3. 考虑添加 x86_64 架构的构建（如果需要原生 Intel 支持）
4. 更新项目的 Xcode 配置文件，永久添加 OpenSSL 路径

## 相关文件

- `.github/workflows/build.yml` - 主构建流程
- `.github/workflows/build-intel.yml` - arm64 构建（Rosetta 支持）
- `WechatExporter.xcodeproj/project.pbxproj` - Xcode 项目配置（未修改）
