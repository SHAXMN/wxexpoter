# 微信图片解密技术备注

## 问题概述

微信在本地存储图片时使用 `wxgf` 格式进行加密，导致无法直接在系统中打开这些图片。

## 加密格式分析

### 文件结构

```
+------------------+
| wxgf 头部 (4B)   |  0x77 0x78 0x67 0x66
+------------------+
| 元数据区         |  约 120-140 字节
| (长度可变)       |
+------------------+
| 加密的图片数据   |  XOR 加密
+------------------+
```

### 加密参数

- **文件标识**: `wxgf` (0x77 0x78 0x67 0x66)
- **加密算法**: XOR
- **密钥**: 0xFE (固定)
- **数据偏移**: 通常在 0x7F-0x8A 之间（不固定）

### 解密方法

```python
# 伪代码
offset = find_jpeg_header(encrypted_data)  # 搜索 0xFF 0xD8 被加密后的位置
xor_key = encrypted_data[offset] ^ 0xFF    # 推断密钥

decrypted = []
for i in range(offset, len(encrypted_data)):
    decrypted.append(encrypted_data[i] ^ xor_key)
```

## 当前实现

### 解密工具: `decrypt_wechat_images.py`

**功能**:
- 自动检测 wxgf 格式
- 搜索加密的 JPEG 头部
- 推断 XOR 密钥
- 解密并保存图片

**使用方法**:
```bash
python3 decrypt_wechat_images.py <输入文件或目录> [输出目录]
```

### 测试结果

#### 成功部分
- ✅ 正确识别 wxgf 格式
- ✅ 成功找到加密偏移量
- ✅ 正确推断 XOR 密钥 (0xFE)
- ✅ `file` 命令识别解密后的文件为 "JPEG image data"

#### 失败部分
- ❌ macOS 预览应用无法打开解密后的图片
- ❌ 双击图片显示"无法打开"错误

### 测试文件

```
测试文件位置:
~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/
  com.tencent.xinWeChat/2.0b4.0.9/*/Message/MessageTemp/*/Image/*.pic.dftemp.jpg

测试样本:
1. 4632.pic.dftemp.jpg (52,869 字节) -> 偏移 0x0080, 密钥 0xFE
2. 9094.pic.dftemp.jpg (11,616 字节) -> 偏移 0x007F, 密钥 0xFE
3. 79813.pic.dftemp.jpg (89,536 字节) -> 偏移 0x0084, 密钥 0xFE
```

## 问题分析

### 可能的原因

#### 1. JPEG 文件结构不完整
- JPEG 文件应该以 `0xFF 0xD8` 开头，`0xFF 0xD9` 结尾
- 可能缺少 EOI (End of Image) 标记
- 需要验证：
  ```bash
  xxd decrypted.jpg | tail -5
  # 检查是否有 0xFF 0xD9
  ```

#### 2. 文件头部有多余数据
- 解密偏移量可能不够精确
- 图片数据前可能还有额外的元数据
- 需要尝试不同的偏移量

#### 3. 加密方式更复杂
- 可能不是简单的固定密钥 XOR
- 可能使用了流密码或分块加密
- 不同区域可能使用不同的密钥

#### 4. 图片元数据损坏
- EXIF 数据可能被破坏
- JFIF/APP0 段可能有问题
- 需要使用 `exiftool` 或 `jpeginfo` 检查

### 验证步骤

```bash
# 1. 检查文件完整性
file decrypted.jpg
jpeginfo -c decrypted.jpg

# 2. 查看文件头部和尾部
xxd decrypted.jpg | head -10
xxd decrypted.jpg | tail -10

# 3. 尝试修复
convert decrypted.jpg -strip fixed.jpg  # ImageMagick
jpegtran -copy none -optimize decrypted.jpg > fixed.jpg

# 4. 使用其他工具打开
open -a "Google Chrome" decrypted.jpg
```

## 已知问题

### 微信版本差异
- 不同版本的微信可能使用不同的加密方式
- 测试环境：微信 8.0.x on iOS 15.0
- 需要测试更多版本

### 文件类型
- 当前只测试了 JPEG 格式
- PNG、GIF 等格式可能有不同的加密方式

## 替代方案

### 方案 1: 使用微信 PC 版
- 在 PC 版微信中打开图片
- 右键保存到本地
- 优点：简单可靠
- 缺点：需要手动操作

### 方案 2: 从 iTunes 备份提取
- 某些图片可能在备份中未加密
- 查找位置：`Favorites/data/` 目录
- 优点：可能获得原始图片
- 缺点：不是所有图片都有备份

### 方案 3: 使用第三方工具
- iMazing
- AnyTrans
- Dr.Fone
- 优点：功能完整
- 缺点：需要付费

### 方案 4: 逆向工程微信
- 反编译微信应用
- 分析加密/解密代码
- 优点：彻底解决问题
- 缺点：技术难度高，可能违反 ToS

## 下一步行动（待后续处理）

### 短期（1-2小时）
- [ ] 使用 `jpeginfo` 检查解密后文件的完整性
- [ ] 尝试使用 ImageMagick 修复图片
- [ ] 测试不同的图片查看器（Chrome、Firefox）

### 中期（1天）
- [ ] 分析更多样本文件
- [ ] 尝试不同的偏移量和密钥
- [ ] 研究 JPEG 文件格式规范

### 长期（1周+）
- [ ] 逆向分析微信应用
- [ ] 研究微信加密算法的演变
- [ ] 开发更完善的解密工具

## 参考资料

### JPEG 格式
- [JPEG File Interchange Format](https://www.w3.org/Graphics/JPEG/jfif3.pdf)
- [JPEG Marker Codes](https://www.disktuna.com/list-of-jpeg-markers/)

### 微信相关
- [WechatExport-iOS](https://github.com/stomakun/WechatExport-iOS)
- [微信数据库解密](https://github.com/ppwwyyxx/wechat-dump)

### 工具
- `file` - 文件类型识别
- `xxd` - 十六进制查看器
- `jpeginfo` - JPEG 文件验证
- `exiftool` - 元数据查看
- `ImageMagick` - 图片处理

## 更新日志

### 2026-04-17
- 初始版本
- 记录解密算法和测试结果
- 分析可能的问题原因
- 列出替代方案和下一步行动
