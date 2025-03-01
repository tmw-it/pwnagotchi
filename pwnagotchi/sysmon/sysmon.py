    def get_font(self, size):
        """Get a font of specified size, falling back to default if necessary"""
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            return ImageFont.load_default()
            
    def draw_metric(self, title, value, warning_threshold=60, critical_threshold=80):
        """Draw a metric with title, value, bar graph, and history"""
        # Create new image with background color
        image = Image.new('RGB', (self.width, self.height), SYSMON_COLORS['graph']['background'])
        draw = ImageDraw.Draw(image)
        
        # Get fonts
        title_font = self.get_font(14)
        value_font = self.get_font(16)
        
        # Calculate bar dimensions (centered)
        bar_width = 20
        bar_height = 50
        bar_x = (self.width - bar_width) // 2
        bar_y = 15  # Moved up to make room for title below
        
        # Draw current value centered above bar
        value_str = f"{value:.1f}%"
        value_w = value_font.getlength(value_str)
        value_x = (self.width - value_w) // 2
        draw.text((value_x, 2), value_str, 
                 font=value_font, fill=SYSMON_COLORS['text']['value'])
        
        # Determine color based on thresholds
        if value >= critical_threshold:
            bar_color = SYSMON_COLORS[title.lower()]['critical']
        elif value >= warning_threshold:
            bar_color = SYSMON_COLORS[title.lower()]['warning']
        else:
            bar_color = SYSMON_COLORS[title.lower()]['normal']
        
        # Draw bar background
        draw.rectangle([(bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height)],
                      outline=SYSMON_COLORS['graph']['grid'])
        
        # Draw bar fill
        fill_height = int(bar_height * (value / 100))
        draw.rectangle([(bar_x, bar_y + bar_height - fill_height),
                       (bar_x + bar_width, bar_y + bar_height)],
                      fill=bar_color)
        
        # Draw title centered below bar
        title_w = title_font.getlength(title)
        title_x = (self.width - title_w) // 2
        draw.text((title_x, bar_y + bar_height + 2), title, 
                 font=title_font, fill=SYSMON_COLORS['text']['title'])
        
        # Draw history graph
        if self.history:
            graph_x = 5
            graph_y = self.height - 15
            graph_width = self.width - 10
            graph_height = 10
            
            # Draw graph background and border
            draw.rectangle([(graph_x, graph_y),
                          (graph_x + graph_width, graph_y + graph_height)],
                         outline=SYSMON_COLORS['graph']['grid'])
            
            # Draw history line
            points = []
            for i, h in enumerate(self.history[-30:]):  # Last 30 readings
                x = graph_x + (i * (graph_width / 30))
                y = graph_y + graph_height - (h * graph_height / 100)
                points.append((x, y))
            
            if len(points) > 1:
                draw.line(points, fill=SYSMON_COLORS['graph']['line'], width=1)
        
        return image