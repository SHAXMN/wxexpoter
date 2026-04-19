# GitHub Actions 构建错误修复说明

## 问题分析

### 1. C++ 标准版本不匹配 (最严重)
- **错误**: `error: "C++ versions less than C++17 are not supported."`
- **原因**: 项目使用 C++14 (`gnu++14`),但 protobuf 的新版本依赖 abseil 库,而 abseil 强制要求 C++17+
- **影响**: 导致大量编译错误,如 `std::invoke`, `std::conjunction`, `std::apply` 等 C++17 特性找不到

### 2. 缺少 silk 音频库
- **错误**: `fatal error: 'silk/SKP_Silk_SDK_API.h' file not found`
- **原因**: silk 是微信语音消息使用的音频编解码库,需要单独编译安装
- **来源**: https://github.com/collects/silk

### 3. silk 库编译错误 (新增)
- **错误**: `clang: error: unknown argument: '-enable-threads'`
- **原因**: silk 库的 Makefile 使用了 gcc 特定的参数,但 macOS 使用 clang 编译器
- **解决**: 使用 sed 移除 `-enable-threads` 参数

### 4. 缺少其他音频库
- **缺少**: opencore-amr (AMR 音频编解码)
- **缺少**: lame (MP3 编解码)

### 5. macOS 部署目标版本警告
- **警告**: `MACOSX_DEPLOYMENT_TARGET` 设置为 10.10,但支持范围是 10.13-26.2.99
- **影响**: 虽然是警告,但可能导致兼容性问题

## 修复方案

### 1. 升级 C++ 标准到 C++17
修改 `WechatExporter.xcodeproj/project.pbxproj`:
```
CLANG_CXX_LANGUAGE_STANDARD = "gnu++14";  →  CLANG_CXX_LANGUAGE_STANDARD = "gnu++17";
```

### 2. 升级 macOS 部署目标
修改 `WechatExporter.xcodeproj/project.pbxproj`:
```
MACOSX_DEPLOYMENT_TARGET = 10.10;  →  MACOSX_DEPLOYMENT_TARGET = 10.13;
```

### 3. 更新 GitHub Actions 工作流
修改 `.github/workflows/build.yml`:

#### 添加依赖安装:
- opencore-amr (AMR 音频编解码)
- lame (MP3 编解码)
- 克隆并编译 silk 库

#### 修复 silk 编译问题:
```bash
# 修复 Makefile 以兼容 clang (移除 -enable-threads 参数)
sed -i '' 's/-enable-threads//g' Makefile
```

#### 更新构建路径:
- 添加 opencore-amr 和 lame 的头文件和库文件路径
- 添加 silk 库的路径 (/usr/local/include/silk, /usr/local/lib)

## 修改的文件

1. **WechatExporter.xcodeproj/project.pbxproj**
   - C++ 标准: gnu++14 → gnu++17
   - macOS 部署目标: 10.10 → 10.13

2. **.github/workflows/build.yml**
   - 添加 opencore-amr, lame 依赖
   - 添加 silk 库的克隆和编译步骤
   - 修复 silk Makefile 的 clang 兼容性问题
   - 更新头文件和库文件搜索路径

## 验证步骤

1. 提交修改到 Git 仓库
2. 推送到 GitHub 触发 Actions
3. 检查构建日志,确认:
   - silk 库成功编译和安装
   - C++17 特性正常使用
   - 所有依赖库正确链接
   - 最终生成 WechatExporter.app

## 提交历史

- **Commit 1** (390b1dd): 修复 C++17 和依赖库问题
- **Commit 2** (4177998): 修复 silk 库编译错误

## 注意事项

- silk 库需要从源码编译,首次构建会稍慢
- C++17 要求 macOS 10.13+,不再支持更旧的系统
- 所有音频编解码库 (silk, opencore-amr, lame) 都是必需的,用于处理微信语音消息
- silk 库的 Makefile 需要修复才能在 macOS (clang) 上编译
