#!/usr/bin/env python3
"""
Script to generate icons for the Mwareeth application.

This script creates various icons for the Mwareeth application, including:
- Main application icon
- Function-specific icons (add person, add relationship, etc.)

The icons are saved to the mwareeth/gui/assets/icons directory.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import math

# Ensure the script can be run from any directory
script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
project_root = script_dir.parent
icons_dir = project_root / "mwareeth" / "gui" / "assets" / "icons"

# Create the icons directory if it doesn't exist
icons_dir.mkdir(parents=True, exist_ok=True)

# Define colors
COLORS = {
    "primary": "#2E7D32",  # Green - representing growth, family tree
    "secondary": "#1565C0",  # Blue - representing trust, stability
    "accent": "#C62828",  # Red - for important actions
    "neutral": "#424242",  # Dark gray - for general UI elements
    "light": "#F5F5F5",  # Light gray - for backgrounds
    "white": "#FFFFFF",  # White - for text and highlights
    "black": "#000000",  # Black - for text and outlines
    "gold": "#FFD700",  # Gold - representing value, inheritance
    "teal": "#00796B",  # Teal - for calculation-related icons
    "purple": "#6A1B9A",  # Purple - for relationship-related icons
    "islamic_green": "#009000",  # Islamic green - cultural significance
}

# Helper functions
def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill, outline=outline, width=width)
    draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill, outline=outline, width=width)
    draw.pieslice((x1, y1, x1 + radius * 2, y1 + radius * 2), 180, 270, fill=fill, outline=outline, width=width)
    draw.pieslice((x2 - radius * 2, y1, x2, y1 + radius * 2), 270, 360, fill=fill, outline=outline, width=width)
    draw.pieslice((x1, y2 - radius * 2, x1 + radius * 2, y2), 90, 180, fill=fill, outline=outline, width=width)
    draw.pieslice((x2 - radius * 2, y2 - radius * 2, x2, y2), 0, 90, fill=fill, outline=outline, width=width)

def draw_islamic_pattern(draw, size, color, complexity=5, line_width=2):
    """Draw an Islamic geometric pattern."""
    width, height = size
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 3
    
    # Draw a star pattern
    points = []
    for i in range(complexity * 2):
        angle = math.pi * i / complexity
        r = radius if i % 2 == 0 else radius // 2
        x = center_x + int(math.cos(angle) * r)
        y = center_y + int(math.sin(angle) * r)
        points.append((x, y))
    
    # Connect all points to create the pattern
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            draw.line([points[i], points[j]], fill=color, width=line_width)

def draw_tree_symbol(draw, xy, size, color, line_width=2):
    """Draw a simple tree symbol representing a family tree."""
    x, y, width, height = xy[0], xy[1], size[0], size[1]
    
    # Draw trunk
    trunk_width = width // 5
    trunk_height = height // 2
    draw.rectangle((x + width//2 - trunk_width//2, y + height - trunk_height, 
                   x + width//2 + trunk_width//2, y + height), 
                   fill=color)
    
    # Draw branches (triangular top)
    draw.polygon([(x, y + height - trunk_height), 
                 (x + width//2, y), 
                 (x + width, y + height - trunk_height)], 
                 fill=color)

def draw_inheritance_symbol(draw, xy, size, color, line_width=2):
    """Draw a symbol representing Islamic inheritance (document with Islamic symbols)."""
    x, y, width, height = xy[0], xy[1], size[0], size[1]
    
    # Draw document
    create_rounded_rectangle(draw, (x, y, x + width, y + height), radius=width//10, fill=None, outline=color, width=line_width)
    
    # Draw crescent moon (Islamic symbol)
    moon_radius = min(width, height) // 5
    moon_x = x + width // 2
    moon_y = y + height // 3
    
    # Outer circle
    draw.ellipse((moon_x - moon_radius, moon_y - moon_radius, 
                 moon_x + moon_radius, moon_y + moon_radius), 
                 outline=color, width=line_width)
    
    # Inner circle (slightly offset to create crescent)
    inner_radius = moon_radius * 0.8
    offset = moon_radius * 0.4
    draw.ellipse((moon_x - inner_radius + offset, moon_y - inner_radius, 
                 moon_x + inner_radius + offset, moon_y + inner_radius), 
                 fill=color, outline=color, width=line_width)
    
    # Draw division lines (representing shares)
    # Horizontal division
    draw.line([(x + width//6, y + height*2//3), 
              (x + width*5//6, y + height*2//3)], 
              fill=color, width=line_width)
    
    # Vertical divisions (creating unequal shares - representing Islamic inheritance portions)
    third_point = x + width // 3
    two_thirds_point = x + width * 2 // 3
    
    draw.line([(third_point, y + height*2//3), 
              (third_point, y + height*5//6)], 
              fill=color, width=line_width)
    
    draw.line([(two_thirds_point, y + height*2//3), 
              (two_thirds_point, y + height*5//6)], 
              fill=color, width=line_width)
    
    # Add small Arabic-style text suggestion (simplified)
    text_y = y + height*5//6 + line_width
    
    # Left portion (smallest)
    small_text_width = (third_point - x - width//6) // 2
    draw.line([(x + width//6 + small_text_width//2, text_y), 
              (x + width//6 + small_text_width, text_y - small_text_width//2)], 
              fill=color, width=line_width)
    
    # Middle portion (largest)
    draw.line([(third_point + (two_thirds_point - third_point)//2, text_y), 
              (third_point + (two_thirds_point - third_point)//2, text_y - small_text_width)], 
              fill=color, width=line_width)
    
    # Right portion (medium)
    draw.line([(two_thirds_point + (x + width*5//6 - two_thirds_point)//2, text_y), 
              (two_thirds_point + (x + width*5//6 - two_thirds_point)//2, text_y - small_text_width*3//4)], 
              fill=color, width=line_width)

def draw_calculation_symbol(draw, xy, size, color, line_width=2):
    """Draw a symbol representing calculation (calculator or math symbols)."""
    x, y, width, height = xy[0], xy[1], size[0], size[1]
    
    # Draw calculator outline
    create_rounded_rectangle(draw, (x, y, x + width, y + height), radius=width//10, fill=None, outline=color, width=line_width)
    
    # Draw display
    display_height = height // 4
    create_rounded_rectangle(draw, (x + width//10, y + height//10, x + width - width//10, y + display_height), 
                           radius=width//20, fill=None, outline=color, width=line_width)
    
    # Draw buttons
    button_size = min(width, height) // 5
    button_spacing = button_size // 4
    start_x = x + width//10
    start_y = y + display_height + height//10
    
    for row in range(3):
        for col in range(3):
            button_x = start_x + col * (button_size + button_spacing)
            button_y = start_y + row * (button_size + button_spacing)
            draw.rectangle((button_x, button_y, button_x + button_size, button_y + button_size), 
                          outline=color, width=line_width)

def draw_person_symbol(draw, xy, size, color, gender=None, line_width=2):
    """Draw a symbol representing a person."""
    x, y, width, height = xy[0], xy[1], size[0], size[1]
    
    # Draw head
    head_radius = min(width, height) // 4
    head_center_x = x + width // 2
    head_center_y = y + head_radius + height // 10
    draw.ellipse((head_center_x - head_radius, head_center_y - head_radius, 
                 head_center_x + head_radius, head_center_y + head_radius), 
                 outline=color, width=line_width)
    
    # Draw body
    body_top_y = head_center_y + head_radius
    body_height = height - body_top_y - height // 10
    
    if gender == "male":
        # Draw triangle body for male
        draw.polygon([(head_center_x, body_top_y), 
                     (x + width // 4, y + height - height // 10), 
                     (x + width - width // 4, y + height - height // 10)], 
                     outline=color, width=line_width)
    elif gender == "female":
        # Draw dress/triangle with rounded bottom for female
        draw.polygon([(head_center_x, body_top_y), 
                     (x + width // 5, y + height - height // 4), 
                     (x + width - width // 5, y + height - height // 4)], 
                     outline=color, width=line_width)
        
        # Draw rounded bottom of dress
        draw.arc((x + width // 5, y + height - height // 2, 
                 x + width - width // 5, y + height), 
                 0, 180, fill=color, width=line_width)
    else:
        # Draw rectangle body for neutral
        draw.rectangle((head_center_x - width // 6, body_top_y, 
                       head_center_x + width // 6, y + height - height // 10), 
                       outline=color, width=line_width)

def draw_relationship_symbol(draw, xy, size, color, line_width=2):
    """Draw a symbol representing a relationship (two people connected)."""
    x, y, width, height = xy[0], xy[1], size[0], size[1]
    
    # Draw two people
    person_width = width // 3
    person_height = height // 2
    
    # Person 1 (left)
    draw_person_symbol(draw, (x, y + height//4, person_width, person_height), 
                      (person_width, person_height), color=color, line_width=line_width)
    
    # Person 2 (right)
    draw_person_symbol(draw, (x + width - person_width, y + height//4, person_width, person_height), 
                      (person_width, person_height), color=color, line_width=line_width)
    
    # Draw connecting line/heart
    center_x = x + width // 2
    center_y = y + height // 2
    heart_size = min(width, height) // 6
    
    # Draw heart
    draw.pieslice((center_x - heart_size, center_y - heart_size//2, 
                  center_x, center_y + heart_size//2), 
                  180, 0, outline=color, width=line_width)
    draw.pieslice((center_x, center_y - heart_size//2, 
                  center_x + heart_size, center_y + heart_size//2), 
                  180, 0, outline=color, width=line_width)
    draw.polygon([(center_x - heart_size, center_y), 
                 (center_x, center_y + heart_size), 
                 (center_x + heart_size, center_y)], 
                 outline=color, width=line_width)

# Create main application icon
def create_app_icon(size=(512, 512)):
    """Create the main application icon depicting Islamic estate division across jurisdictions."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Background with subtle Islamic pattern
    bg = Image.new('RGBA', size, hex_to_rgb(COLORS["light"]) + (200,))
    bg_draw = ImageDraw.Draw(bg)
    draw_islamic_pattern(bg_draw, size, hex_to_rgb(COLORS["islamic_green"]) + (80,), complexity=8, line_width=1)
    img = Image.alpha_composite(img, bg)
    draw = ImageDraw.Draw(img)
    
    # Draw a circular background
    circle_radius = min(size) // 2 - 10
    circle_center = (size[0] // 2, size[1] // 2)
    draw.ellipse((circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                 circle_center[0] + circle_radius, circle_center[1] + circle_radius),
                 fill=hex_to_rgb(COLORS["secondary"]) + (230,))
    
    # Calculate sizes
    margin = size[0] // 10
    width = size[0] - 2*margin
    height = size[1] - 2*margin
    
    # Draw a globe/world map (simplified) to represent different jurisdictions
    globe_radius = circle_radius * 0.7
    globe_center_x = circle_center[0]
    globe_center_y = circle_center[1]
    
    # Draw globe outline
    draw.ellipse((globe_center_x - globe_radius, globe_center_y - globe_radius,
                 globe_center_x + globe_radius, globe_center_y + globe_radius),
                 fill=hex_to_rgb(COLORS["white"]) + (255,),
                 outline=hex_to_rgb(COLORS["neutral"]) + (255,), width=3)
    
    # Draw latitude lines
    for i in range(1, 4):
        y_offset = globe_radius * i / 4
        # Draw horizontal ellipses (latitude lines)
        draw.ellipse((globe_center_x - globe_radius, globe_center_y - y_offset,
                     globe_center_x + globe_radius, globe_center_y + y_offset),
                     outline=hex_to_rgb(COLORS["neutral"]) + (100,), width=1)
    
    # Draw longitude lines
    for i in range(1, 6):
        angle = math.pi * i / 6
        x1 = globe_center_x - int(globe_radius * math.cos(angle))
        y1 = globe_center_y - int(globe_radius * math.sin(angle))
        x2 = globe_center_x + int(globe_radius * math.cos(angle))
        y2 = globe_center_y + int(globe_radius * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=hex_to_rgb(COLORS["neutral"]) + (100,), width=1)
    
    # Draw regions/jurisdictions (simplified)
    # These are abstract shapes representing different regions/jurisdictions
    regions = [
        [(0.2, 0.3), (0.4, 0.2), (0.5, 0.4), (0.3, 0.5)],  # Region 1
        [(0.6, 0.2), (0.8, 0.3), (0.7, 0.5), (0.5, 0.4)],  # Region 2
        [(0.3, 0.5), (0.5, 0.4), (0.7, 0.5), (0.6, 0.8), (0.4, 0.8)],  # Region 3
    ]
    
    region_colors = [
        hex_to_rgb(COLORS["primary"]) + (180,),
        hex_to_rgb(COLORS["teal"]) + (180,),
        hex_to_rgb(COLORS["gold"]) + (180,)
    ]
    
    for i, region in enumerate(regions):
        points = []
        for px, py in region:
            x = globe_center_x + int(globe_radius * (px * 2 - 1))
            y = globe_center_y + int(globe_radius * (py * 2 - 1))
            points.append((x, y))
        draw.polygon(points, fill=region_colors[i % len(region_colors)])
    
    # Draw division lines across regions (representing inheritance division)
    for i in range(1, 4):
        angle = math.pi * (i / 4 + 0.1)
        x1 = globe_center_x - int(globe_radius * math.cos(angle))
        y1 = globe_center_y - int(globe_radius * math.sin(angle))
        x2 = globe_center_x + int(globe_radius * math.cos(angle))
        y2 = globe_center_y + int(globe_radius * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=hex_to_rgb(COLORS["white"]) + (200,), width=3)
    
    # Draw Islamic symbol (crescent and star) at the top
    crescent_radius = globe_radius * 0.25
    crescent_x = globe_center_x
    crescent_y = globe_center_y - globe_radius * 0.6
    
    # Outer circle of crescent
    draw.ellipse((crescent_x - crescent_radius, crescent_y - crescent_radius,
                 crescent_x + crescent_radius, crescent_y + crescent_radius),
                 outline=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=3)
    
    # Inner circle (slightly offset to create crescent)
    inner_radius = crescent_radius * 0.8
    offset = crescent_radius * 0.4
    draw.ellipse((crescent_x - inner_radius + offset, crescent_y - inner_radius,
                 crescent_x + inner_radius + offset, crescent_y + inner_radius),
                 fill=hex_to_rgb(COLORS["islamic_green"]) + (255,),
                 outline=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=3)
    
    # Draw star
    star_radius = crescent_radius * 0.4
    star_x = crescent_x + crescent_radius * 1.2
    star_y = crescent_y
    
    # Draw 5-pointed star
    star_points = []
    for i in range(5):
        # Outer points
        angle = math.pi/2 + i * 2*math.pi/5
        x = star_x + star_radius * math.cos(angle)
        y = star_y + star_radius * math.sin(angle)
        star_points.append((x, y))
        
        # Inner points
        angle += math.pi/5
        inner_radius = star_radius * 0.4
        x = star_x + inner_radius * math.cos(angle)
        y = star_y + inner_radius * math.sin(angle)
        star_points.append((x, y))
    
    draw.polygon(star_points, fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # Draw inheritance document at the bottom
    doc_width = globe_radius * 0.8
    doc_height = globe_radius * 0.6
    doc_x = globe_center_x - doc_width/2
    doc_y = globe_center_y + globe_radius * 0.5
    
    # Document outline
    create_rounded_rectangle(draw, (doc_x, doc_y, doc_x + doc_width, doc_y + doc_height),
                           radius=doc_width//20, fill=hex_to_rgb(COLORS["light"]) + (230,),
                           outline=hex_to_rgb(COLORS["neutral"]) + (255,), width=3)
    
    # Division lines (representing shares)
    # Horizontal division
    draw.line([(doc_x + doc_width//10, doc_y + doc_height//2),
              (doc_x + doc_width*9//10, doc_y + doc_height//2)],
              fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=3)
    
    # Vertical divisions (creating unequal shares - representing Islamic inheritance portions)
    third_point = doc_x + doc_width // 3
    two_thirds_point = doc_x + doc_width * 2 // 3
    
    draw.line([(third_point, doc_y + doc_height//2),
              (third_point, doc_y + doc_height*9//10)],
              fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=3)
    
    draw.line([(two_thirds_point, doc_y + doc_height//2),
              (two_thirds_point, doc_y + doc_height*9//10)],
              fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=3)
    
    # Add fraction numbers to represent inheritance shares
    fraction_y = doc_y + doc_height * 3/4
    
    # 1/8 (small share)
    small_x = doc_x + doc_width//6
    draw.text((small_x, fraction_y - doc_height//10), "1", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    draw.line([(small_x - doc_width//20, fraction_y), (small_x + doc_width//20, fraction_y)],
             fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=2)
    draw.text((small_x, fraction_y + doc_height//10), "8", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # 1/2 (large share)
    mid_x = doc_x + doc_width//2
    draw.text((mid_x, fraction_y - doc_height//10), "1", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    draw.line([(mid_x - doc_width//20, fraction_y), (mid_x + doc_width//20, fraction_y)],
             fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=2)
    draw.text((mid_x, fraction_y + doc_height//10), "2", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # 1/4 (medium share)
    large_x = doc_x + doc_width*5//6
    draw.text((large_x, fraction_y - doc_height//10), "1", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    draw.line([(large_x - doc_width//20, fraction_y), (large_x + doc_width//20, fraction_y)],
             fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=2)
    draw.text((large_x, fraction_y + doc_height//10), "4", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # Save in different sizes
    for icon_size in [16, 32, 48, 64, 128, 256, 512]:
        resized_img = img.resize((icon_size, icon_size), Image.LANCZOS)
        resized_img.save(icons_dir / f"app_icon_{icon_size}.png")
    
    # Create ICO file for Windows
    img.save(icons_dir / "app_icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)])
    
    # Create a favicon
    favicon = img.resize((32, 32), Image.LANCZOS)
    favicon.save(icons_dir / "favicon.ico", format="ICO")
    
    return img

# Create function-specific icons
def create_add_person_icon(size=(20, 20)):
    """Create an icon for adding a person with Islamic inheritance context."""
    # Create a larger image for better detail, then resize
    large_size = (size[0] * 3, size[1] * 3)
    img = Image.new('RGBA', large_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simpler, more compact design
    margin = large_size[0] // 10
    width = large_size[0] - 2*margin
    height = large_size[1] - 2*margin
    
    # Draw plus sign (more prominent)
    plus_size = width // 2
    plus_x = margin + width // 4
    plus_y = margin + height // 4
    plus_thickness = max(3, large_size[0] // 15)
    
    # Draw plus circle background
    draw.ellipse((plus_x, plus_y, plus_x + plus_size, plus_y + plus_size), 
                fill=hex_to_rgb(COLORS["secondary"]) + (255,))
    
    # Draw plus symbol
    draw.rectangle((plus_x + plus_size//4, plus_y + plus_size//2 - plus_thickness//2,
                   plus_x + plus_size - plus_size//4, plus_y + plus_size//2 + plus_thickness//2),
                   fill=hex_to_rgb(COLORS["white"]) + (255,))
    draw.rectangle((plus_x + plus_size//2 - plus_thickness//2, plus_y + plus_size//4,
                   plus_x + plus_size//2 + plus_thickness//2, plus_y + plus_size - plus_size//4),
                   fill=hex_to_rgb(COLORS["white"]) + (255,))
    
    # Draw person silhouette (simplified)
    person_x = margin + width // 2
    person_y = margin + height // 2
    person_size = min(width, height) // 2
    
    # Person head
    head_radius = person_size // 4
    head_center_x = person_x + person_size // 2
    head_center_y = person_y + head_radius
    draw.ellipse((head_center_x - head_radius, head_center_y - head_radius, 
                 head_center_x + head_radius, head_center_y + head_radius), 
                 fill=hex_to_rgb(COLORS["accent"]) + (255,))
    
    # Person body (simplified)
    body_top_y = head_center_y + head_radius
    body_width = head_radius * 1.5
    body_height = person_size // 2
    draw.rectangle((head_center_x - body_width//2, body_top_y, 
                   head_center_x + body_width//2, body_top_y + body_height), 
                   fill=hex_to_rgb(COLORS["accent"]) + (255,))
    
    # Resize to target size
    img = img.resize(size, Image.LANCZOS)
    img.save(icons_dir / "add_person.png")
    return img

def create_add_relationship_icon(size=(20, 20)):
    """Create an icon for adding a family relationship in Islamic context."""
    # Create a larger image for better detail, then resize
    large_size = (size[0] * 3, size[1] * 3)
    img = Image.new('RGBA', large_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = large_size[0] // 8
    width = large_size[0] - 2*margin
    height = large_size[1] - 2*margin
    
    # Draw family tree structure (simplified)
    center_x = margin + width // 2
    center_y = margin + height // 2
    
    # Draw parent node
    parent_y = margin + height // 4
    parent_radius = min(width, height) // 10
    draw.ellipse((center_x - parent_radius, parent_y - parent_radius, 
                 center_x + parent_radius, parent_y + parent_radius), 
                 fill=hex_to_rgb(COLORS["purple"]) + (255,))
    
    # Draw connecting line
    line_length = height // 3
    draw.line([(center_x, parent_y + parent_radius), 
              (center_x, parent_y + line_length)], 
              fill=hex_to_rgb(COLORS["purple"]) + (255,), width=3)
    
    # Draw child nodes
    child_y = parent_y + line_length + parent_radius
    child_spacing = width // 3
    child_radius = parent_radius
    
    # Left child
    draw.ellipse((center_x - child_spacing//2 - child_radius, child_y - child_radius, 
                 center_x - child_spacing//2 + child_radius, child_y + child_radius), 
                 fill=hex_to_rgb(COLORS["purple"]) + (255,))
    
    # Right child
    draw.ellipse((center_x + child_spacing//2 - child_radius, child_y - child_radius, 
                 center_x + child_spacing//2 + child_radius, child_y + child_radius), 
                 fill=hex_to_rgb(COLORS["purple"]) + (255,))
    
    # Draw connecting lines to children
    draw.line([(center_x, parent_y + line_length), 
              (center_x - child_spacing//2, child_y)], 
              fill=hex_to_rgb(COLORS["purple"]) + (255,), width=3)
    
    draw.line([(center_x, parent_y + line_length), 
              (center_x + child_spacing//2, child_y)], 
              fill=hex_to_rgb(COLORS["purple"]) + (255,), width=3)
    
    # Draw Islamic pattern in background (subtle)
    pattern_radius = min(width, height) // 2
    pattern_x = margin + width // 2
    pattern_y = margin + height // 2
    
    for i in range(8):
        angle = math.pi * i / 4
        x1 = pattern_x + int(pattern_radius * 0.7 * math.cos(angle))
        y1 = pattern_y + int(pattern_radius * 0.7 * math.sin(angle))
        x2 = pattern_x + int(pattern_radius * 0.7 * math.cos(angle + math.pi))
        y2 = pattern_y + int(pattern_radius * 0.7 * math.sin(angle + math.pi))
        draw.line([(x1, y1), (x2, y2)], fill=hex_to_rgb(COLORS["purple"]) + (100,), width=1)
    
    # Draw plus sign
    plus_size = large_size[0] // 5
    plus_x = large_size[0] - plus_size - margin // 2
    plus_y = margin // 2
    plus_thickness = max(2, large_size[0] // 24)
    
    # Draw plus circle background
    draw.ellipse((plus_x, plus_y, plus_x + plus_size, plus_y + plus_size), 
                fill=hex_to_rgb(COLORS["accent"]) + (255,))
    
    # Draw plus symbol
    draw.rectangle((plus_x + plus_size//4, plus_y + plus_size//2 - plus_thickness//2,
                   plus_x + plus_size - plus_size//4, plus_y + plus_size//2 + plus_thickness//2),
                   fill=hex_to_rgb(COLORS["white"]) + (255,))
    draw.rectangle((plus_x + plus_size//2 - plus_thickness//2, plus_y + plus_size//4,
                   plus_x + plus_size//2 + plus_thickness//2, plus_y + plus_size - plus_size//4),
                   fill=hex_to_rgb(COLORS["white"]) + (255,))
    
    # Resize to target size
    img = img.resize(size, Image.LANCZOS)
    img.save(icons_dir / "add_relationship.png")
    return img

def create_calculate_inheritance_icon(size=(20, 20)):
    """Create an icon for calculating Islamic inheritance."""
    # Create a larger image for better detail, then resize
    large_size = (size[0] * 3, size[1] * 3)
    img = Image.new('RGBA', large_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = large_size[0] // 8
    width = large_size[0] - 2*margin
    height = large_size[1] - 2*margin
    
    # Draw calculator base
    calc_x = margin
    calc_y = margin
    calc_width = width
    calc_height = height
    
    # Calculator body
    create_rounded_rectangle(draw, (calc_x, calc_y, calc_x + calc_width, calc_y + calc_height), 
                           radius=calc_width//10, fill=hex_to_rgb(COLORS["teal"]) + (230,), 
                           outline=hex_to_rgb(COLORS["neutral"]) + (255,), width=3)
    
    # Calculator display
    display_height = calc_height // 4
    display_margin = calc_width // 20
    create_rounded_rectangle(draw, (calc_x + display_margin, calc_y + display_margin, 
                                  calc_x + calc_width - display_margin, calc_y + display_height), 
                           radius=display_margin//2, fill=hex_to_rgb(COLORS["light"]) + (255,), 
                           outline=hex_to_rgb(COLORS["neutral"]) + (255,), width=2)
    
    # Draw Islamic inheritance fractions on the display
    # 1/2, 1/4, 1/8 - common Quranic shares
    text_y = calc_y + display_height // 2
    fraction_spacing = (calc_width - 2*display_margin) // 4
    
    # Draw 1/2
    half_x = calc_x + display_margin + fraction_spacing
    numerator_y = text_y - display_margin
    denominator_y = text_y + display_margin
    line_y = text_y
    line_width = fraction_spacing // 2
    line_thickness = 2
    
    # 1
    draw.text((half_x, numerator_y), "1", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    # Line
    draw.line([(half_x - line_width//4, line_y), (half_x + line_width//4, line_y)], 
              fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=line_thickness)
    # 2
    draw.text((half_x, denominator_y), "2", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # Draw 1/4
    quarter_x = calc_x + display_margin + 2*fraction_spacing
    # 1
    draw.text((quarter_x, numerator_y), "1", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    # Line
    draw.line([(quarter_x - line_width//4, line_y), (quarter_x + line_width//4, line_y)], 
              fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=line_thickness)
    # 4
    draw.text((quarter_x, denominator_y), "4", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # Draw 1/8
    eighth_x = calc_x + display_margin + 3*fraction_spacing
    # 1
    draw.text((eighth_x, numerator_y), "1", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    # Line
    draw.line([(eighth_x - line_width//4, line_y), (eighth_x + line_width//4, line_y)], 
              fill=hex_to_rgb(COLORS["islamic_green"]) + (255,), width=line_thickness)
    # 8
    draw.text((eighth_x, denominator_y), "8", fill=hex_to_rgb(COLORS["islamic_green"]) + (255,))
    
    # Draw calculator buttons (simplified)
    button_start_y = calc_y + display_height + display_margin
    button_size = (calc_height - display_height - 2*display_margin) // 4
    button_margin = button_size // 6
    
    for row in range(4):
        for col in range(3):
            button_x = calc_x + display_margin + col * (button_size + button_margin)
            button_y = button_start_y + row * (button_size + button_margin)
            
            button_color = hex_to_rgb(COLORS["light"]) + (255,)
            if row == 3 and col == 1:  # Special color for equals button
                button_color = hex_to_rgb(COLORS["gold"]) + (255,)
            
            draw.rectangle((button_x, button_y, button_x + button_size, button_y + button_size), 
                          fill=button_color, outline=hex_to_rgb(COLORS["neutral"]) + (255,), width=1)
    
    # Resize to target size
    img = img.resize(size, Image.LANCZOS)
    img.save(icons_dir / "calculate_inheritance.png")
    return img

def create_visualize_tree_icon(size=(20, 20)):
    """Create an icon for visualizing the family tree (standard refresh/view icon)."""
    # Create a larger image for better detail, then resize
    large_size = (size[0] * 3, size[1] * 3)
    img = Image.new('RGBA', large_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = large_size[0] // 8
    width = large_size[0] - 2*margin
    height = large_size[1] - 2*margin
    
    # Draw a standard refresh icon (circular arrow)
    center_x = margin + width // 2
    center_y = margin + height // 2
    radius = min(width, height) // 2
    
    # Draw circular arrow
    # Define points for the arrow path
    arrow_points = []
    start_angle = 45  # degrees
    end_angle = 315   # degrees
    
    for angle in range(start_angle, end_angle, 5):
        rad = math.radians(angle)
        x = center_x + int(radius * math.cos(rad))
        y = center_y + int(radius * math.sin(rad))
        arrow_points.append((x, y))
    
    # Draw the arc
    if len(arrow_points) > 1:
        draw.line(arrow_points, fill=hex_to_rgb(COLORS["secondary"]) + (255,), width=large_size[0]//12)
    
    # Draw arrowhead
    arrow_size = radius // 2
    arrow_angle = math.radians(start_angle - 15)  # Angle for arrowhead
    arrow_x = center_x + int(radius * math.cos(math.radians(start_angle)))
    arrow_y = center_y + int(radius * math.sin(math.radians(start_angle)))
    
    # Calculate arrowhead points
    point1 = (arrow_x, arrow_y)
    point2 = (arrow_x - int(arrow_size * math.cos(arrow_angle - math.pi/6)), 
              arrow_y - int(arrow_size * math.sin(arrow_angle - math.pi/6)))
    point3 = (arrow_x - int(arrow_size * math.cos(arrow_angle + math.pi/6)), 
              arrow_y - int(arrow_size * math.sin(arrow_angle + math.pi/6)))
    
    # Draw arrowhead
    draw.polygon([point1, point2, point3], fill=hex_to_rgb(COLORS["secondary"]) + (255,))
    
    # Resize to target size
    img = img.resize(size, Image.LANCZOS)
    img.save(icons_dir / "visualize_tree.png")
    return img

def create_save_load_icon(size=(20, 20)):
    """Create an icon for saving/loading family trees."""
    # Create a larger image for better detail, then resize
    large_size = (size[0] * 3, size[1] * 3)
    img = Image.new('RGBA', large_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    margin = large_size[0] // 8
    width = large_size[0] - 2*margin
    height = large_size[1] - 2*margin
    
    # Draw file/document base
    file_x = margin
    file_y = margin
    file_width = width * 3 // 4
    file_height = height
    
    # Draw file base with light fill
    create_rounded_rectangle(draw, (file_x, file_y, file_x + file_width, file_y + file_height), 
                           radius=file_width//10, fill=hex_to_rgb(COLORS["light"]) + (230,), 
                           outline=hex_to_rgb(COLORS["neutral"]) + (255,), width=3)
    
    # Draw folded corner
    fold_size = file_width // 4
    draw.polygon([(file_x + file_width - fold_size, file_y), 
                 (file_x + file_width, file_y + fold_size), 
                 (file_x + file_width, file_y), 
                 (file_x + file_width - fold_size, file_y)], 
                 fill=hex_to_rgb(COLORS["neutral"]) + (200,))
    draw.line([(file_x + file_width - fold_size, file_y), 
              (file_x + file_width - fold_size, file_y + fold_size), 
              (file_x + file_width, file_y + fold_size)], 
              fill=hex_to_rgb(COLORS["neutral"]) + (255,), width=3)
    
    # Draw family tree symbol inside file (simplified)
    tree_margin = file_width // 8
    tree_width = file_width - 2*tree_margin
    tree_height = file_height // 2
    tree_x = file_x + tree_margin
    tree_y = file_y + file_height // 4
    
    # Draw tree trunk
    trunk_width = tree_width // 5
    trunk_height = tree_height // 2
    draw.rectangle((tree_x + tree_width//2 - trunk_width//2, tree_y + tree_height - trunk_height, 
                   tree_x + tree_width//2 + trunk_width//2, tree_y + tree_height), 
                   fill=hex_to_rgb(COLORS["primary"]) + (255,))
    
    # Draw tree top (triangle)
    draw.polygon([(tree_x, tree_y + tree_height - trunk_height), 
                 (tree_x + tree_width//2, tree_y), 
                 (tree_x + tree_width, tree_y + tree_height - trunk_height)], 
                 fill=hex_to_rgb(COLORS["primary"]) + (255,))
    
    # Draw arrow for save/load action
    arrow_width = width // 3
    arrow_height = height // 2
    arrow_x = file_x + file_width - arrow_width // 3
    arrow_y = file_y + file_height // 2 - arrow_height // 2
    
    # Arrow shaft
    shaft_width = arrow_width // 2
    shaft_height = arrow_height // 4
    draw.rectangle((arrow_x, arrow_y + arrow_height//2 - shaft_height//2,
                   arrow_x + shaft_width, arrow_y + arrow_height//2 + shaft_height//2),
                   fill=hex_to_rgb(COLORS["secondary"]) + (255,))
    
    # Arrow head
    head_size = arrow_width // 2
    draw.polygon([(arrow_x + shaft_width, arrow_y + arrow_height//2 - head_size//2),
                 (arrow_x + shaft_width + head_size, arrow_y + arrow_height//2),
                 (arrow_x + shaft_width, arrow_y + arrow_height//2 + head_size//2)],
                 fill=hex_to_rgb(COLORS["secondary"]) + (255,))
    
    # Resize to target size
    img = img.resize(size, Image.LANCZOS)
    img.save(icons_dir / "save_load.png")
    return img

def create_male_icon(size=(20, 20)):
    """Create an icon representing a male person."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw male symbol
    margin = size[0] // 8
    width = size[0] - 2*margin
    height = size[1] - 2*margin
    draw_person_symbol(draw, (margin, margin, width, height), 
                      (width, height), hex_to_rgb(COLORS["secondary"]) + (255,), gender="male", line_width=2)
    
    img.save(icons_dir / "male.png")
    return img

def create_female_icon(size=(20, 20)):
    """Create an icon representing a female person."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw female symbol
    margin = size[0] // 8
    width = size[0] - 2*margin
    height = size[1] - 2*margin
    draw_person_symbol(draw, (margin, margin, width, height), 
                      (width, height), hex_to_rgb(COLORS["accent"]) + (255,), gender="female", line_width=2)
    
    img.save(icons_dir / "female.png")
    return img

def create_deceased_icon(size=(20, 20)):
    """Create an icon representing a deceased person."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw person symbol
    margin = size[0] // 8
    width = size[0] - 2*margin
    height = size[1] - 2*margin
    draw_person_symbol(draw, (margin, margin, width, height), 
                      (width, height), hex_to_rgb(COLORS["neutral"]) + (200,), line_width=2)
    
    # Draw RIP text or cross symbol
    cross_size = size[0] // 3
    cross_x = size[0] - cross_size - margin
    cross_y = size[1] - cross_size - margin
    cross_thickness = max(2, size[0] // 32)
    
    # Draw cross
    draw.rectangle((cross_x + cross_size//2 - cross_thickness//2, cross_y,
                   cross_x + cross_size//2 + cross_thickness//2, cross_y + cross_size),
                   fill=hex_to_rgb(COLORS["black"]) + (200,))
    draw.rectangle((cross_x, cross_y + cross_size//3,
                   cross_x + cross_size, cross_y + cross_size//3 + cross_thickness),
                   fill=hex_to_rgb(COLORS["black"]) + (200,))
    
    img.save(icons_dir / "deceased.png")
    return img

def create_all_icons():
    """Create all icons for the application."""
    print("Generating application icons...")
    
    # Create main application icon
    app_icon = create_app_icon()
    print(f"Created main application icon in various sizes")
    
    # Create function-specific icons
    create_add_person_icon()
    print("Created add person icon")
    
    create_add_relationship_icon()
    print("Created add relationship icon")
    
    create_calculate_inheritance_icon()
    print("Created calculate inheritance icon")
    
    create_visualize_tree_icon()
    print("Created visualize tree icon")
    
    create_save_load_icon()
    print("Created save/load icon")
    
    # Create gender icons
    create_male_icon()
    print("Created male icon")
    
    create_female_icon()
    print("Created female icon")
    
    create_deceased_icon()
    print("Created deceased icon")
    
    print(f"All icons have been saved to: {icons_dir}")

if __name__ == "__main__":
    create_all_icons()
