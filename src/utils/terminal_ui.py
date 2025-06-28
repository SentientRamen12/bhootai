import time
import os
import sys
from typing import Optional
from pathlib import Path

class TerminalUI:
    def __init__(self):
        self.terminal_width = self._get_terminal_width()
    
    def _get_terminal_width(self) -> int:
        """Get terminal width, default to 80 if can't determine"""
        try:
            return os.get_terminal_size().columns
        except:
            return 80
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_centered(self, text: str, char: str = " "):
        """Print text centered with optional character padding"""
        padding = (self.terminal_width - len(text)) // 2
        if padding < 0:
            padding = 0
        print(f"{char * padding}{text}{char * padding}")
    
    def print_separator(self, char: str = "="):
        """Print a separator line"""
        print(char * self.terminal_width)
    
    def print_box(self, text: str, title: Optional[str] = None):
        """Print text in a box with optional title"""
        # Calculate maximum box width (80% of terminal width, max 80 chars)
        max_box_width = min(int(self.terminal_width * 0.8), 80)
        content_width = max_box_width - 4  # Account for borders and padding
        
        # Split text into lines that fit within content width
        lines = []
        for paragraph in text.split('\n'):
            if len(paragraph) <= content_width:
                lines.append(paragraph)
            else:
                # Word wrap the paragraph
                words = paragraph.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= content_width:
                        current_line += (" " + word) if current_line else word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
        
        # Calculate actual box width based on content
        max_line_width = max(len(line) for line in lines) if lines else 0
        box_width = max(max_line_width + 4, 60, len(title) + 4 if title else 60)
        
        # Top border
        print("┌" + "─" * (box_width - 2) + "┐")
        
        # Title if provided
        if title:
            title_line = f"│ {title.center(box_width - 4)} │"
            print(title_line)
            print("├" + "─" * (box_width - 2) + "┤")
        
        # Content
        for line in lines:
            padded_line = line.ljust(box_width - 4)
            print(f"│ {padded_line} │")
        
        # Bottom border
        print("└" + "─" * (box_width - 2) + "┘")
    
    def show_loading_screen(self):
        """Show animated loading screen"""
        self.clear_screen()
        
        loading_frames = [
            "🌙 Initializing the cursed realm...",
            "🌙 Loading ancient memories...",
            "🌙 Summoning the Dungeon Master...",
            "🌙 Preparing your nightmare...",
            "🌙 The realm is ready..."
        ]
        
        for i, frame in enumerate(loading_frames):
            self.clear_screen()
            print("\n" * 3)
            self.print_centered("🌙 BHOOT AI - HORROR TEXT RPG 🌙")
            print()
            self.print_centered("Welcome to the cursed realm where nightmares take form...")
            print()
            self.print_centered(frame)
            print()
            
            # Progress bar
            progress = (i + 1) / len(loading_frames)
            bar_width = 40
            filled = int(bar_width * progress)
            bar = "█" * filled + "░" * (bar_width - filled)
            self.print_centered(f"[{bar}] {int(progress * 100)}%")
            
            time.sleep(0.8)
        
        time.sleep(1)
    
    def show_title_screen(self):
        """Show the main title screen"""
        self.clear_screen()
        print("\n" * 2)
        
        # ASCII art title for BHOOT AI
        title_art = """
██████╗ ██╗  ██╗ ██████╗  ██████╗ ███████╗      █████╗ ██╗
██╔══██╗██║  ██║██╔═══██╗██╔═══██╗   ██╔═╝     ██╔══██╗██║
██████╔╝███████║██║   ██║██║   ██║   ██║       ███████║██║
██╔══██╗██╔══██║██║   ██║██║   ██║   ██║       ██╔══██║██║
██████╔╝██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║  ██║██║
╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝
        """
        
        for line in title_art.strip().split('\n'):
            self.print_centered(line)
        
        print()
        
        self.print_centered("You have been drawn into a world of unspeakable horrors.")
        self.print_centered("Your sanity and survival hang by a thread.")
        print()
        self.print_separator("=")
    
    def get_player_name(self) -> str:
        """Get player name with styled input"""
        print("\n" + "="*50)
        print("🌙 CHARACTER CREATION 🌙")
        print("="*50)
        print("Before you enter the nightmare, tell us your name...")
        print("="*50)
        
        while True:
            name = input("\nEnter your character's name: ").strip()
            if name:
                return name
            print("Please enter a valid name.")
    
    def show_chapter_header(self, chapter_num: int, title: str, description: str):
        """Show chapter header with description"""
        self.clear_screen()
        print("\n" * 2)
        
        # Chapter number
        self.print_centered(f"CHAPTER {chapter_num}")
        print()
        
        # Chapter title
        self.print_centered(f"🌙 {title} 🌙")
        print()
        
        # Chapter description in a box
        self.print_box(description)
        print()
    
    def show_interaction(self, player_name: str, dm_response: str, interaction_num: int):
        """Show a single interaction between player and DM"""
        print(f"\n{'='*60}")
        print(f"INTERACTION {interaction_num}")
        print(f"{'='*60}")
        
        # DM response in a styled box
        print("\n🌙 DUNGEON MASTER 🌙")
        self.print_box(dm_response)
        print()
        
        # Player input area
        print(f"💀 {player_name.upper()} 💀")
        print("What do you do?")
        print("-" * 40)
    
    def show_player_message(self, player_name: str, message: str):
        """Show player's message"""
        print(f"\n💀 {player_name}: {message}")
        print("-" * 40)
    
    def show_dm_response(self, response: str):
        """Show DM's response"""
        print("\n🌙 DUNGEON MASTER:")
        self.print_box(response)
        print()
    
    def show_progress(self, interaction_count: int, plot_status: dict):
        """Show progress update"""
        print(f"\n{'='*50}")
        print(f"📜 PROGRESS UPDATE - Interaction {interaction_count}")
        print(f"{'='*50}")
        print(f"Plot Points Completed: {plot_status['completed_points']}/{plot_status['total_points']}")
        print(f"Current Plot: {plot_status['current_point']}")
        print(f"{'='*50}")
        input("Press Enter to continue...")
        self.clear_screen()
    
    def show_exit_screen(self, player_name: str, interaction_count: int, plot_status: dict):
        """Show exit screen with session summary"""
        self.clear_screen()
        print("\n" * 3)
        
        self.print_centered("🌙 SESSION ENDED 🌙")
        print()
        
        # Session summary in a box
        summary = f"""
Player: {player_name}
Total Interactions: {interaction_count}
Plot Points Completed: {plot_status['completed_points']}/{plot_status['total_points']}
Current Plot: {plot_status['current_point']}

The nightmare fades... until next time.
        """.strip()
        
        self.print_box(summary, "Session Summary")
        print()
        
        self.print_centered("Thank you for playing BHOOT AI")
        print()
        input("Press Enter to exit...")
    
    def show_error_message(self, error: str):
        """Show error message"""
        print(f"\n❌ ERROR: {error}")
        print("The Dungeon Master stutters, trying to recover...")
        input("Press Enter to continue...")
    
    def animate_text(self, text: str, delay: float = 0.03):
        """Animate text appearing character by character"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print() 