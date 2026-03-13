# -*- coding: utf-8 -*-
"""
Create simple test images for Nova 2 Omni testing
This creates placeholder images when real photos aren't available
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_construction_site_image():
    """Create a simple construction site placeholder"""
    img = Image.new('RGB', (800, 600), color='#87CEEB')  # Sky blue
    draw = ImageDraw.Draw(img)
    
    # Draw ground
    draw.rectangle([0, 400, 800, 600], fill='#8B7355')  # Brown ground
    
    # Draw building under construction
    draw.rectangle([200, 200, 600, 400], fill='#808080', outline='black', width=3)
    
    # Draw scaffolding
    for x in range(200, 600, 50):
        draw.line([x, 200, x, 400], fill='yellow', width=2)
    for y in range(200, 400, 50):
        draw.line([200, y, 600, y], fill='yellow', width=2)
    
    # Draw crane
    draw.line([650, 100, 650, 400], fill='red', width=5)
    draw.line([650, 100, 750, 150], fill='red', width=5)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((250, 300), "CONSTRUCTION", fill='white', font=font)
    draw.text((300, 350), "SITE", fill='white', font=font)
    
    # Add safety sign
    draw.rectangle([50, 450, 200, 550], fill='yellow', outline='black', width=3)
    draw.text((70, 480), "SAFETY", fill='black')
    draw.text((80, 510), "FIRST", fill='black')
    
    return img

def create_permit_document_image():
    """Create a simple permit document placeholder"""
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([50, 50, 750, 950], outline='black', width=3)
    
    # Add header
    draw.rectangle([50, 50, 750, 150], fill='#4169E1')  # Royal blue
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_medium = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except:
        font_large = font_medium = font_small = ImageFont.load_default()
    
    draw.text((200, 80), "BUILDING PERMIT", fill='white', font=font_large)
    
    # Add permit details
    y = 200
    details = [
        "Permit Number: BMC/2026/12345",
        "Project Name: Green City Phase 3",
        "Location: Andheri West, Mumbai",
        "Permit Type: Construction",
        "Issue Date: March 1, 2026",
        "Expiry Date: March 1, 2028",
        "Issuing Authority: BMC Mumbai",
        "",
        "Special Conditions:",
        "- Safety barriers required",
        "- Working hours: 8 AM - 6 PM",
        "- Noise limits apply",
    ]
    
    for detail in details:
        draw.text((100, y), detail, fill='black', font=font_small)
        y += 40
    
    # Add stamp
    draw.ellipse([550, 700, 700, 850], outline='red', width=3)
    draw.text((570, 760), "APPROVED", fill='red', font=font_medium)
    
    return img

def create_safety_violation_image():
    """Create a safety violation placeholder"""
    img = Image.new('RGB', (800, 600), color='#87CEEB')
    draw = ImageDraw.Draw(img)
    
    # Draw ground
    draw.rectangle([0, 400, 800, 600], fill='#8B7355')
    
    # Draw unsafe construction site (no barriers)
    draw.rectangle([200, 250, 600, 400], fill='#808080', outline='black', width=3)
    
    # Draw open pit (hazard)
    draw.ellipse([100, 450, 300, 580], fill='#654321', outline='black', width=3)
    
    # Draw warning sign
    draw.polygon([(650, 450), (750, 450), (700, 550)], fill='yellow', outline='black')
    
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
    
    draw.text((680, 480), "!", fill='red', font=font)
    
    # Add text
    draw.text((50, 50), "SAFETY VIOLATION:", fill='red', font=font)
    draw.text((50, 100), "No barriers around pit", fill='red')
    draw.text((50, 130), "No safety signage", fill='red')
    
    return img

def main():
    """Create test images"""
    print("🎨 Creating test images for Nova 2 Omni...\n")
    
    # Create sample_images directory if it doesn't exist
    os.makedirs('sample_images', exist_ok=True)
    
    # Create images
    images = [
        ('construction_site_1.jpg', create_construction_site_image()),
        ('permit_document_1.jpg', create_permit_document_image()),
        ('safety_violation_1.jpg', create_safety_violation_image()),
    ]
    
    for filename, img in images:
        filepath = os.path.join('sample_images', filename)
        img.save(filepath)
        print(f"✓ Created: {filepath}")
    
    print(f"\n✅ Created {len(images)} test images")
    print("💡 Run 'python agents/image_analysis_nova.py' to analyze them")
    print("💡 Or add your own real images to sample_images/ folder")

if __name__ == "__main__":
    main()
