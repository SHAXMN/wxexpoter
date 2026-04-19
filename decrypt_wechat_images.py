#!/usr/bin/env python3
"""
微信 wxgf 格式图片解密工具 - 改进版
支持批量解密，自动检测密钥和偏移量
"""
import os
import sys
from pathlib import Path
from typing import Optional, Tuple


def detect_image_format(data: bytes) -> Tuple[str, bool]:
    """
    检测图片格式

    Returns:
        (扩展名, 是否有效)
    """
    if len(data) < 4:
        return 'unknown', False

    # JPEG - 只需要检查前两个字节和第三个字节是 0xFF
    if data[:2] == b'\xff\xd8' and len(data) >= 3 and data[2] == 0xff:
        return 'jpg', True

    # PNG
    if len(data) >= 8 and data[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png', True

    # GIF
    if len(data) >= 6 and data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif', True

    # BMP
    if data[:2] == b'BM':
        return 'bmp', True

    # WebP
    if len(data) >= 12 and data[8:12] == b'WEBP':
        return 'webp', True

    return 'unknown', False


def find_jpeg_header(data: bytes, max_search: int = 8192) -> Optional[Tuple[int, int]]:
    """
    在加密数据中查找 JPEG 头部

    Returns:
        (偏移量, XOR密钥) 或 None
    """
    search_limit = min(max_search, len(data) - 20)

    for offset in range(search_limit):
        if offset + 1 >= len(data):
            break

        byte1 = data[offset]
        byte2 = data[offset + 1]

        # 假设原始数据是 JPEG (0xFF 0xD8)
        key1 = byte1 ^ 0xFF
        key2 = byte2 ^ 0xD8

        if key1 == key2:
            # 验证解密后的数据
            xor_key = key1
            decrypted_preview = bytes([data[i] ^ xor_key for i in range(offset, min(offset + 100, len(data)))])

            # 检查是否是有效的 JPEG（放宽验证）
            if decrypted_preview[:2] == b'\xff\xd8':
                # 进一步验证：检查第3-4字节是否是有效的 JPEG 标记
                if len(decrypted_preview) >= 4 and decrypted_preview[2] == 0xff:
                    return offset, xor_key

    return None


def decrypt_wxgf_file(input_path: Path, output_dir: Optional[Path] = None, verbose: bool = True) -> bool:
    """
    解密单个 wxgf 文件

    Args:
        input_path: 输入文件路径
        output_dir: 输出目录（默认为输入文件所在目录）
        verbose: 是否输出详细信息

    Returns:
        是否成功解密
    """
    if not input_path.exists():
        if verbose:
            print(f"❌ 文件不存在: {input_path}")
        return False

    # 读取文件
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()

    # 检查是否是 wxgf 格式
    if not encrypted_data.startswith(b'wxgf'):
        if verbose:
            print(f"⚠️  {input_path.name} 不是 wxgf 格式，跳过")
        return False

    if verbose:
        print(f"\n处理: {input_path.name}")
        print(f"  文件大小: {len(encrypted_data):,} 字节")

    # 查找 JPEG 头部
    result = find_jpeg_header(encrypted_data)

    if result is None:
        if verbose:
            print(f"  ❌ 无法找到有效的图片数据")
        return False

    offset, xor_key = result

    if verbose:
        print(f"  ✓ 找到加密数据")
        print(f"    偏移量: 0x{offset:04X} ({offset} 字节)")
        print(f"    XOR 密钥: 0x{xor_key:02X}")

    # 解密
    decrypted = bytearray()
    for i in range(offset, len(encrypted_data)):
        decrypted.append(encrypted_data[i] ^ xor_key)

    # 检测格式
    ext, is_valid = detect_image_format(bytes(decrypted))

    if not is_valid:
        if verbose:
            print(f"  ❌ 解密后的数据不是有效的图片格式")
        return False

    # 确定输出路径
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{input_path.stem}_decrypted.{ext}"

    # 写入文件
    with open(output_path, 'wb') as f:
        f.write(decrypted)

    if verbose:
        print(f"  ✓ 解密成功: {output_path.name}")
        print(f"    输出大小: {len(decrypted):,} 字节")

    return True


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python decrypt_wechat_images.py <文件或目录> [输出目录]")
        print()
        print("示例:")
        print("  python decrypt_wechat_images.py image.jpg")
        print("  python decrypt_wechat_images.py /path/to/images/")
        print("  python decrypt_wechat_images.py /path/to/images/ /path/to/output/")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not input_path.exists():
        print(f"❌ 路径不存在: {input_path}")
        sys.exit(1)

    success_count = 0
    fail_count = 0
    skip_count = 0

    if input_path.is_file():
        # 单个文件
        if decrypt_wxgf_file(input_path, output_dir):
            success_count = 1
        else:
            fail_count = 1

    elif input_path.is_dir():
        # 目录
        print(f"扫描目录: {input_path}")

        # 查找所有图片文件
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp']:
            image_files.extend(input_path.glob(ext))
            image_files.extend(input_path.glob(ext.upper()))

        if not image_files:
            print("❌ 目录中没有找到图片文件")
            sys.exit(1)

        print(f"找到 {len(image_files)} 个图片文件\n")

        for file_path in sorted(image_files):
            result = decrypt_wxgf_file(file_path, output_dir, verbose=True)

            if result:
                success_count += 1
            elif file_path.name.endswith('_decrypted.jpg'):
                skip_count += 1
            else:
                # 检查是否已经是解密的文件
                with open(file_path, 'rb') as f:
                    header = f.read(4)
                if not header.startswith(b'wxgf'):
                    skip_count += 1
                else:
                    fail_count += 1

    else:
        print(f"❌ 无效的路径: {input_path}")
        sys.exit(1)

    # 输出统计
    print("\n" + "=" * 50)
    print("解密完成")
    print("=" * 50)
    print(f"✓ 成功: {success_count}")
    print(f"⊘ 跳过: {skip_count}")
    print(f"✗ 失败: {fail_count}")
    print(f"总计: {success_count + skip_count + fail_count}")


if __name__ == '__main__':
    main()
