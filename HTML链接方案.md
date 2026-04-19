# WechatExporter 附件 HTML 链接方案

**日期**: 2026-04-19  
**目标**: 在 HTML 聊天记录中显示文档附件链接  
**用户需求**: 接受文件名为 msgId，但需要在 HTML 中正确链接

---

## 🎯 方案选择

### 方案 A: 逆向 protobuf 获取原始文件名（难度高）

**可行性**: ⚠️ 可能，但困难

**技术路径**:
1. 使用 WechatExporter 已有的 `RawMessage` 类
2. 尝试不同的字段编号组合
3. 找到存储文件名的字段

**挑战**:
- 需要逆向工程微信的 protobuf 结构
- 字段编号未知，需要大量试错
- 不同微信版本可能有不同的结构

**预计时间**: 1-2 周  
**成功率**: 50%

---

### 方案 B: 直接链接附件（msgId 作为文件名）（推荐）

**可行性**: ✅ 高度可行

**技术路径**:
1. 在消息解析时，检测 Type 49 (APPMSG) 消息
2. 尝试解析 XML 获取文件扩展名
3. 如果解析失败，检查 OpenData 目录是否有对应的文件
4. 在 HTML 中生成链接：`../attachments/{sessionHash}/{msgId}.{ext}`

**优点**:
- ✅ 不需要逆向 protobuf
- ✅ 立即可实现
- ✅ 用户可以点击下载附件
- ✅ 即使文件名是 msgId，也比没有链接好

**预计时间**: 2-3 小时  
**成功率**: 95%

---

## 📋 方案 B 详细设计

### 1. 修改消息解析逻辑

在 `MessageParser.cpp` 的 `parseAppMsg()` 函数中：

```cpp
bool MessageParser::parseAppMsg(const WXMSG& msg, ...) 
{
    // 现有代码：尝试解析 XML
    XmlParser xmlParser(msg.content, true);
    
    std::string appMsgTypeStr;
    if (!xmlParser.parseNodeValue("/msg/appmsg/type", appMsgTypeStr))
    {
        // XML 解析失败（可能是压缩格式）
        // 新增：尝试从 OpenData 查找附件
        if (tryParseCompressedAttachment(msg, session, tv))
        {
            return true;
        }
        
        // 原有的回退逻辑
        tv["%%MESSAGE%%"] = m_resManager.getLocaleString("[Link]");
        return true;
    }
    
    // 原有代码继续...
}
```

### 2. 新增函数：尝试解析压缩附件

```cpp
bool MessageParser::tryParseCompressedAttachment(
    const WXMSG& msg, 
    const Session& session, 
    TemplateValues& tv) const
{
    // 检查 OpenData 目录是否有对应的附件
    std::string sessionHash = session.getHash();
    std::string msgId = msg.msgId;
    
    // 查找可能的文件扩展名
    const char* extensions[] = {".pdf", ".doc", ".docx", ".xls", ".xlsx",
                               ".ppt", ".pptx", ".zip", ".rar", ".7z"};
    
    for (const char* ext : extensions)
    {
        std::string vpath = m_userBase + "/OpenData/" + sessionHash + "/" + msgId + ext;
        
        // 检查文件是否存在
        const ITunesFile* file = m_iTunesDb.findITunesFile(vpath);
        if (file != nullptr)
        {
            // 找到附件！
            // 复制到 attachments 目录
            std::string destDir = combinePath(m_outputPath, "attachments", sessionHash);
            if (!existsDirectory(destDir))
            {
                makeDirectory(destDir);
            }
            
            std::string filename = msgId + ext;
            if (m_iTunesDb.copyFile(vpath, destDir, filename))
            {
                // 生成 HTML 链接
                tv.setName("plainshare");
                tv["%%SHARINGURL%%"] = "../attachments/" + sessionHash + "/" + filename;
                tv["%%SHARINGTITLE%%"] = getFileTypeLabel(ext); // "PDF 文档", "Word 文档" 等
                tv["%%MESSAGE%%"] = "";
                tv["%%MSGTYPE%%"] = "file";
                
                return true;
            }
        }
    }
    
    return false;
}

// 辅助函数：获取文件类型标签
std::string MessageParser::getFileTypeLabel(const std::string& ext) const
{
    if (ext == ".pdf") return m_resManager.getLocaleString("PDF Document");
    if (ext == ".doc" || ext == ".docx") return m_resManager.getLocaleString("Word Document");
    if (ext == ".xls" || ext == ".xlsx") return m_resManager.getLocaleString("Excel Spreadsheet");
    if (ext == ".ppt" || ext == ".pptx") return m_resManager.getLocaleString("PowerPoint Presentation");
    if (ext == ".zip" || ext == ".rar" || ext == ".7z") return m_resManager.getLocaleString("Archive");
    return m_resManager.getLocaleString("File");
}
```

### 3. HTML 模板修改

在 HTML 模板中，附件链接会显示为：

```html
<div class="msg media left">
    <div class="file-attachment">
        <a href="../attachments/00addb0e6b1aa10505e0ff9910b8af40/123456.pdf" download>
            <span class="file-icon">📄</span>
            <span class="file-name">PDF 文档</span>
        </a>
    </div>
</div>
```

### 4. 用户体验

**导出后的效果**:
- 聊天记录中显示："📄 PDF 文档"
- 点击链接下载文件：`123456.pdf`
- 文件可以正常打开

**优点**:
- ✅ 用户可以直接在聊天记录中点击下载
- ✅ 知道附件类型（PDF、Word 等）
- ✅ 文件按时间顺序显示在聊天记录中

**缺点**:
- ❌ 文件名是 msgId（如 `123456.pdf`），不是原始名称（如 `项目报告.pdf`）

---

## 🔄 方案 B 的改进版：混合方案

### 思路

1. **优先尝试解析 XML**（获取原始文件名）
2. **如果失败，使用 msgId 作为文件名**（仍然生成链接）

### 实现

```cpp
bool MessageParser::parseAppMsgAttachment(const WXAPPMSG& appMsg, ...) const
{
    std::string title;
    std::string attachFileExtName;
    
    // 尝试解析 XML
    xmlParser.parseNodeValue("/msg/appmsg/title", title);
    xmlParser.parseNodeValue("/msg/appmsg/appattach/fileext", attachFileExtName);
    
    if (attachFileExtName.empty())
    {
        // XML 解析失败，尝试从 OpenData 推断扩展名
        attachFileExtName = detectExtensionFromOpenData(appMsg.msg->msgId, session.getHash());
    }
    
    if (attachFileExtName.empty())
    {
        // 完全无法确定文件类型
        return false;
    }
    
    // 构建文件路径
    std::string attachFileName = m_userBase + "/OpenData/" + session.getHash() + "/" + appMsg.msg->msgId;
    std::string attachOutputFileName = appMsg.msg->msgId;
    
    if (!attachFileExtName.empty())
    {
        attachFileName += "." + attachFileExtName;
        attachOutputFileName += "." + attachFileExtName;
    }
    
    // 复制文件到 attachments 目录
    std::string destDir = combinePath(m_outputPath, "attachments", session.getHash());
    if (!existsDirectory(destDir))
    {
        makeDirectory(destDir);
    }
    
    if (m_iTunesDb.copyFile(attachFileName, destDir, attachOutputFileName))
    {
        // 生成 HTML 链接
        tv.setName("plainshare");
        tv["%%SHARINGURL%%"] = "../attachments/" + session.getHash() + "/" + attachOutputFileName;
        
        // 如果有原始文件名，使用它；否则使用类型标签
        if (!title.empty())
        {
            tv["%%SHARINGTITLE%%"] = title;
        }
        else
        {
            tv["%%SHARINGTITLE%%"] = getFileTypeLabel("." + attachFileExtName);
        }
        
        tv["%%MESSAGE%%"] = "";
        tv["%%MSGTYPE%%"] = "file";
        
        return true;
    }
    
    return false;
}
```

---

## 📊 方案对比

| 特性 | 方案 A（逆向 protobuf） | 方案 B（直接链接） | 混合方案 |
|------|----------------------|------------------|---------|
| **原始文件名** | ✅ 可能获取 | ❌ 无法获取 | ⚠️ 部分获取 |
| **HTML 链接** | ✅ 有 | ✅ 有 | ✅ 有 |
| **实现难度** | 🔴 高 | 🟢 低 | 🟡 中 |
| **开发时间** | 1-2 周 | 2-3 小时 | 4-6 小时 |
| **成功率** | 50% | 95% | 90% |
| **用户体验** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 推荐方案

### 立即实施：方案 B（直接链接）

**理由**:
1. ✅ 高成功率（95%）
2. ✅ 快速实现（2-3 小时）
3. ✅ 满足用户需求（HTML 中有链接）
4. ✅ 可以后续升级到混合方案

### 未来改进：混合方案

在方案 B 的基础上：
1. 尝试解析 XML 获取原始文件名
2. 如果成功，使用原始文件名
3. 如果失败，回退到 msgId

### 长期目标：方案 A（逆向 protobuf）

如果有时间和资源：
1. 研究微信消息的 protobuf 结构
2. 找到文件名字段
3. 完美解决问题

---

## 🚀 实施步骤（方案 B）

### 步骤 1: 修改 MessageParser.h

添加新方法声明：

```cpp
bool tryParseCompressedAttachment(const WXMSG& msg, const Session& session, TemplateValues& tv) const;
std::string detectExtensionFromOpenData(const std::string& msgId, const std::string& sessionHash) const;
std::string getFileTypeLabel(const std::string& ext) const;
```

### 步骤 2: 修改 MessageParser.cpp

1. 在 `parseAppMsg()` 中添加回退逻辑
2. 实现 `tryParseCompressedAttachment()`
3. 实现 `detectExtensionFromOpenData()`
4. 实现 `getFileTypeLabel()`

### 步骤 3: 修改 parseAppMsgAttachment()

改为复制到 `attachments/` 目录，而不是 `assets/` 目录。

### 步骤 4: 测试

1. 编译项目
2. 导出聊天记录
3. 检查 HTML 中是否有附件链接
4. 点击链接验证下载

---

## 📋 预期结果

### HTML 显示效果

```html
<!-- 成功解析 XML 的附件 -->
<div class="msg media left">
    <a href="../attachments/00addb0e6b1aa10505e0ff9910b8af40/123456.pdf">
        📄 项目报告.pdf
    </a>
</div>

<!-- 无法解析 XML 的附件 -->
<div class="msg media left">
    <a href="../attachments/00addb0e6b1aa10505e0ff9910b8af40/789012.docx">
        📄 Word 文档
    </a>
</div>
```

### 用户体验

1. 打开聊天记录 HTML
2. 看到附件消息（带图标和标签）
3. 点击链接
4. 浏览器下载文件（文件名可能是 msgId）
5. 打开文件查看内容

---

## ✅ 总结

### 推荐：方案 B（直接链接）

**优点**:
- ✅ 快速实现（2-3 小时）
- ✅ 高成功率（95%）
- ✅ 满足用户需求
- ✅ 可以点击下载

**缺点**:
- ❌ 文件名是 msgId

**结论**: 这是最实用的方案，可以立即解决问题。

### 您的选择

请告诉我您希望：
1. **立即实施方案 B**（直接链接，msgId 作为文件名）
2. **尝试混合方案**（先尝试解析 XML，失败则用 msgId）
3. **探索方案 A**（逆向 protobuf，获取原始文件名）

我可以立即开始实施您选择的方案！

---

**报告生成时间**: 2026-04-19  
**推荐方案**: 方案 B（直接链接）  
**预计时间**: 2-3 小时
