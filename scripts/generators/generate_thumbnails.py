from PIL import Image, ImageDraw, ImageFont
import os

class ThumbnailGenerator:
    """Generate article thumbnails without Canva API"""
    
    def __init__(self, output_dir='news/thumbnails'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Load league colors
        try:
            import json
            # Try multiple paths
            paths = ['data/league_one_colors_v2.json', '../data/league_one_colors_v2.json', 'league_colors.json', '../league_colors.json']
            for p in paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        self.league_colors = json.load(f)
                    break
            if not hasattr(self, 'league_colors'): self.league_colors = {}
        except:
            self.league_colors = {}
    
    def create_thumbnail(self, title, category, league_name=None, output_filename=None):
        """Create a simple but professional thumbnail"""
        
        if category == 'player':
            # Player Banner Mode
            width, height = 1200, 250
            font_size_large = 130
            # Team name badge font
            font_size_team = 40
        else:
            # Standard News Mode
            width, height = 1200, 630
            font_size_large = 60
            font_size_small = 30
        
        # Get colors based on category/league
        bg_color, text_color = self.get_colors(category, league_name)
        
        # Create image
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font, fallback to default
        try:
            # Try to find a clearly Heavy Japanese font
            # Hiragino Sans W8 is good for "Impact"
            font_large_path = '/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc'
            if not os.path.exists(font_large_path):
                # Fallback to W6 if W8 not found
                 font_large_path = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
            
            font_large = ImageFont.truetype(font_large_path, font_size_large)
            font_small = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 30)
            
            if category == 'player':
                font_team = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', font_size_team)
        except:
            # Fallbacks...
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_team = ImageFont.load_default()
        
        if category != 'player':
            # ... (Standard News Logic Omitted for brevity, keep existing) ...
            # Add category badge (Only for news)
            badge_text = self.get_category_badge(category)
            badge_bbox = draw.textbbox((0, 0), badge_text, font=font_small)
            badge_width = badge_bbox[2] - badge_bbox[0] + 40
            badge_height = badge_bbox[3] - badge_bbox[1] + 20
            
            badge_x = 40
            badge_y = 40
            draw.rectangle(
                [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
                fill=text_color
            )
            draw.text(
                (badge_x + 20, badge_y + 10),
                badge_text,
                fill=bg_color,
                font=font_small
            )
            
            # Add site name at bottom
            site_name = "RugbyPick.com"
            draw.text((40, height - 60), site_name, fill=text_color, font=font_small)

            # Add title (word wrap)
            title_lines = self.wrap_text(title, font_large, width - 80)
            y_offset = height // 2 - (len(title_lines) * 70) // 2
            
            for line in title_lines:
                # Center text
                bbox = draw.textbbox((0, 0), line, font=font_large)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                
                # Add shadow for better readability
                draw.text((x + 2, y_offset + 2), line, fill=(0, 0, 0, 128), font=font_large)
                draw.text((x, y_offset), line, fill=text_color, font=font_large)
                y_offset += 80

        else:
            # === PLAYER BANNER SPECIFIC V3 ===
            
            # 3. Draw Player Name (Centered, Large, White Fill, Black Stroke)
            # User Request V5: "English name sticking out. Make text smaller. Fit to frame."
            # "Make it a bit lower".
            # "Text is preferable to image" -> Dynamic Sizing.
            
            # Start with smaller base size
            base_font_size = 110
            font_large = ImageFont.truetype(font_large_path, base_font_size)
            
            # Dynamic Fit
            max_text_width = width - 100 # 50px padding each side
            
            bbox = draw.textbbox((0, 0), title, font=font_large)
            text_w = bbox[2] - bbox[0]
            
            # Loop to shrink
            current_size = base_font_size
            while text_w > max_text_width and current_size > 40:
                current_size -= 5
                font_large = ImageFont.truetype(font_large_path, current_size)
                bbox = draw.textbbox((0, 0), title, font=font_large)
                text_w = bbox[2] - bbox[0]
            
            text_h = bbox[3] - bbox[1]
            
            # Position: Centered horizontally.
            # Vertically: User said "Make it a bit lower". 
            # Previous V4.2 was (height - text_h) / 2 - 50 (Up 50).
            # "Lower" means less negative offset, or positive.
            # Let's try Centered (Offset 0) or slightly Lower (Offset +10).
            # If we align centered, it might overlap team name if player name is huge.
            # But we shrunk the text.
            # Let's try Offset -10 (Slightly Up from Center, but lower than -50).
            text_x = (width - text_w) / 2
            text_y = (height - text_h) / 2 - 10 
            
            # Stroke: Black, 12px
            stroke_width = 12
            draw.text((text_x, text_y), title, font=font_large, fill="white", stroke_width=stroke_width, stroke_fill="black")

            # 4. Draw Team Name (Bottom Right)
            # User Request V4: "Yellow(Color) outside white frame team name". 
            # User Request V4.2: "Team name matching player name. Lower it but stay in frame."
            if league_name and league_name != "Unknown Team":
                # font_small = ImageFont.truetype(FONT_BOLD, 40) # This is font_team
                t_bbox = draw.textbbox((0, 0), league_name, font=font_team)
                t_w = t_bbox[2] - t_bbox[0]
                t_h = t_bbox[3] - t_bbox[1]
                
                # Position: Bottom Right with padding
                # V4 was tx = width - t_w - 40, ty = height - t_h - 30.
                # User says: "Make it a bit lower".
                # So increase Y.
                # Max Y is height.
                # height = 250.
                # If we put it at height - t_h - 10, it's very close to bottom.
                tx = width - t_w - 40
                ty = height - t_h - 15 # Lower: only 15px from bottom
                
                # Draw Text with White Stroke (Frame)
                # Fill=Black, Stroke=White (Width 6) -> "White frame"
                draw.text((tx, ty), league_name, font=font_team, fill="black", stroke_width=6, stroke_fill="white")

        
        # Save
        if not output_filename:
            output_filename = f"{category}_{hash(title) % 10000}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        img.save(output_path)
        
        return output_path
    
    def get_colors(self, category, league_name):
        """Get colors based on category or league"""
        
        # Try league colors first (league_name is Team Name for players)
        if league_name:
            # Check exact match
            if league_name in self.league_colors:
                c = self.league_colors[league_name]
                return (self.hex_to_rgb(c['primary']), self.hex_to_rgb(c['secondary']))
            
            # Check partial match? No, keys are strict.
            # Fallback for unknown teams if player
            if category == 'player':
                c = self.league_colors.get('default', {"primary": "#333333", "secondary": "#FFFFFF"})
                return (self.hex_to_rgb(c['primary']), self.hex_to_rgb(c['secondary']))
        
        # Category-based colors (News)
        category_colors = {
            'transfer': ('#E60012', '#FFFFFF'),
            'callup': ('#0066CC', '#FFFFFF'),
            'injury': ('#FF6600', '#FFFFFF'),
            'retirement': ('#666666', '#FFFFFF'),
            'match': ('#006633', '#FFFFFF'),
            'general': ('#0097B2', '#FFFFFF')
        }
        
        colors = category_colors.get(category, ('#0097B2', '#FFFFFF'))
        return (self.hex_to_rgb(colors[0]), self.hex_to_rgb(colors[1]))
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def get_category_badge(self, category):
        """Get Japanese badge text for category"""
        badges = {
            'transfer': '移籍',
            'callup': '代表招集',
            'injury': '怪我',
            'retirement': '引退',
            'match': '試合結果',
            'general': 'ニュース'
        }
        return badges.get(category, 'ニュース')
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Limit to 3 lines
        return lines[:3]

def main():
    generator = ThumbnailGenerator()
    
    # Test thumbnails
    test_cases = [
        ("松島幸太朗がクレルモンに移籍", "transfer", "Top 14"),
        ("日本代表メンバー発表", "callup", "League One"),
        ("姫野和樹が負傷離脱", "injury", None),
        ("リーチマイケルが引退表明", "retirement", None),
        ("埼玉が東京に勝利", "match", "League One")
    ]
    
    print("=== Generating Test Thumbnails ===\n")
    
    for title, category, league in test_cases:
        output = generator.create_thumbnail(title, category, league)
        print(f"✓ Created: {output}")
    
    print("\n=== Complete ===")

if __name__ == "__main__":
    main()
