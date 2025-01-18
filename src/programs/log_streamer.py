import re
import time
from pathlib import Path
from src.interfaces.cli import ToolCLI


class LogStreamer:
    def __init__(self, log_file: str):
        self.log_file = Path(log_file)
        self.cli = ToolCLI(menu_text="📜 Log Streamer\n\nStreaming log file updates...")
        self.last_position = 0
        
    def stream(self):
        """Stream new log entries as they're written to the file"""
        self.cli.print_info(f"Starting to stream {self.log_file}")
        
        # Define log pattern matching the exact format from test.log
        pattern = r"(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) \| (?P<level>\w+)\s+ \| (?P<module>__main__):(?P<function><module>):(?P<line>\d+) - (?P<message>.*)"
        
        while True:
            try:
                # Check if file exists and has new content
                if not self.log_file.exists():
                    self.cli.print_error(f"Log file {self.log_file} not found")
                    return
                    
                file_size = self.log_file.stat().st_size
                if file_size > self.last_position:
                    # Read new content
                    try:
                        with open(self.log_file, 'r', encoding='utf-8') as f:
                            f.seek(self.last_position)
                            new_lines = f.readlines()
                            self.last_position = f.tell()
                            
                            # Parse and display each new log entry
                            for line in new_lines:
                                try:
                                    match = re.match(pattern, line.strip())
                                    if match:
                                        self.display_log(match.groupdict())
                                    else:
                                        self.cli.print_error(f"Failed to parse log line: {line.strip()}")
                                except Exception as e:
                                    self.cli.print_error(f"Error parsing log line: {str(e)}")
                    except Exception as e:
                        self.cli.print_error(f"Error reading file: {str(e)}")
                        time.sleep(1)  # Wait before retrying
                        continue
                                
            except KeyboardInterrupt:
                self.cli.print_info("Stopping log streamer")
                break
            except Exception as e:
                self.cli.print_error(f"Error streaming logs: {str(e)}")
                time.sleep(1)  # Wait before retrying
                
    def display_log(self, parsed_log):
        """Display parsed log entry using rich formatting"""
        timestamp = parsed_log['time']
        level = parsed_log['level'].strip()
        module = parsed_log['module']
        function = parsed_log['function']
        line = parsed_log['line']
        message = parsed_log['message']
        
        # Create formatted log entry
        log_text = f"[{timestamp}] {level} {module}:{function}:{line} \n\n {message}"
        
        # Color code based on log level
        if level == "DEBUG":
            style = "bright_blue"
        elif level == "INFO":
            style = "bright_green" 
        elif level == "WARNING":
            style = "bright_yellow"
        elif level == "ERROR":
            style = "bright_red"
        elif level == "CRITICAL":
            style = "bold bright_red"
        else:
            style = "white"
            
        self.cli.print_message(log_text, "Log", style)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Stream and display log files')
    parser.add_argument('log_file', help='Path to log file to stream')
    args = parser.parse_args()
    
    streamer = LogStreamer(args.log_file)
    streamer.stream()

if __name__ == "__main__":
    main()
