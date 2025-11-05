"""
Logo 图片处理脚本
读取现有的 logo.png，检查尺寸并创建优化版本
"""
from pathlib import Path
from PIL import Image
import sys
import numpy as np

def remove_white_background(img, threshold=240):
    """移除白色背景，使其透明"""
    # 转换为 RGBA 模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 转换为 numpy 数组
    data = np.array(img)
    
    # 获取 RGB 通道
    rgb = data[:, :, :3]
    
    # 计算每个像素是否为白色（或接近白色）
    # threshold 是阈值，240 表示 RGB 值都大于 240 的像素被认为是白色
    is_white = np.all(rgb >= threshold, axis=2)
    
    # 设置 alpha 通道：白色区域设为透明（alpha=0），其他区域保持不透明（alpha=255）
    data[:, :, 3] = np.where(is_white, 0, 255)
    
    # 转换回 PIL Image
    return Image.fromarray(data)

def process_logo():
    """处理 logo 图片"""
    logo_path = Path(__file__).parent / "logo.png"
    
    if not logo_path.exists():
        print(f"错误：找不到 {logo_path}")
        return
    
    try:
        # 读取图片
        img = Image.open(logo_path)
        original_size = img.size
        print(f"原始 logo 尺寸: {original_size[0]}x{original_size[1]}")
        print(f"原始格式: {img.format}")
        print(f"原始模式: {img.mode}")
        
        # 检查是否需要调整
        max_dimension = max(original_size)
        
        # 创建优化版本（512x512，正方形，保持比例，透明背景）
        print(f"\n正在创建优化版本（透明背景）...")
        target_size = 512
        
        # 移除白色背景，使其透明
        if img.mode != 'RGBA':
            print("正在移除白色背景...")
            img = remove_white_background(img)
        
        # 计算缩放比例，保持原始宽高比
        ratio = min(target_size / original_size[0], target_size / original_size[1])
        new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
        resized = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # 创建透明背景的正方形画布
        canvas = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
        
        # 居中放置
        offset = ((target_size - new_size[0]) // 2, (target_size - new_size[1]) // 2)
        # 使用 alpha 通道进行粘贴，保持透明效果
        canvas.paste(resized, offset, resized)
        resized = canvas
        
        # 保存优化版本（覆盖原文件）
        resized.save(logo_path, "PNG", optimize=True)
        print(f"已创建优化版本: {logo_path} ({target_size}x{target_size})")
        print(f"原始尺寸: {original_size[0]}x{original_size[1]} -> 优化后: {target_size}x{target_size}")
        
        # 显示图片信息
        print(f"\n图片信息:")
        print(f"   尺寸: {original_size[0]}x{original_size[1]}")
        print(f"   格式: {img.format}")
        print(f"   模式: {img.mode}")
        print(f"   文件大小: {logo_path.stat().st_size / 1024:.2f} KB")
        
    except Exception as e:
        print(f"错误：处理图片时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        process_logo()
    except ImportError:
        print("错误：需要安装 Pillow 库")
        print("请运行: pip install Pillow")
        sys.exit(1)

