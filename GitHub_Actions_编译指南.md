# 使用 GitHub Actions 编译 WechatExporter

## 方案说明

由于您不想安装 Xcode，可以使用 GitHub Actions 在云端编译项目。

## 步骤

### 1. 创建 GitHub 仓库

```bash
cd /Users/HuBin/Documents/Quant/WechatExporter

# 初始化 git（如果还没有）
git init

# 添加所有文件
git add .

# 提交修改
git commit -m "Add document attachment export feature"

# 创建 GitHub 仓库（在 GitHub 网站上）
# 然后关联远程仓库
git remote add origin https://github.com/YOUR_USERNAME/WechatExporter.git
git push -u origin main
```

### 2. 创建 GitHub Actions 工作流

创建文件 `.github/workflows/build.yml`：

```yaml
name: Build WechatExporter

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: macos-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Xcode
      uses: maxim-lobanov/setup-xcode@v1
      with:
        xcode-version: latest-stable
    
    - name: Build
      run: |
        xcodebuild clean build \
          -project WechatExporter.xcodeproj \
          -scheme WechatExporter \
          -configuration Release \
          -derivedDataPath ./build
    
    - name: Package app
      run: |
        cd build/Build/Products/Release
        zip -r WechatExporter.zip WechatExporter.app
    
    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: WechatExporter
        path: build/Build/Products/Release/WechatExporter.zip
```

### 3. 触发编译

1. 推送代码到 GitHub
2. 在 GitHub 仓库页面，点击 "Actions" 标签
3. 点击 "Build WechatExporter" 工作流
4. 点击 "Run workflow"
5. 等待编译完成（约 5-10 分钟）
6. 下载编译产物

### 4. 下载并使用

```bash
# 下载编译好的 WechatExporter.zip
cd ~/Downloads

# 解压
unzip WechatExporter.zip

# 移除隔离属性
xattr -cr WechatExporter.app

# 运行
open WechatExporter.app
```

## 优点

- ✅ 无需本地安装 Xcode
- ✅ 在云端自动编译
- ✅ 可以随时重新编译
- ✅ 免费（GitHub Actions 对公开仓库免费）

## 缺点

- ❌ 需要创建 GitHub 账号
- ❌ 需要上传代码到 GitHub
- ❌ 编译时间较长（5-10 分钟）

## 注意事项

1. **代码隐私**：如果不想公开代码，可以创建私有仓库（GitHub 免费账号支持）
2. **编译限制**：GitHub Actions 每月有免费额度限制
3. **首次设置**：需要一些 Git 和 GitHub 的基础知识
