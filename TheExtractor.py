#!/usr/bin/env python3
import sys
import os
import re
import time

# Reconfigure standard streams to UTF-8 if possible
try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except (AttributeError, Exception):
    pass

# Enable ANSI terminal colors on Windows
if os.name == 'nt':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# UI Color constants
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# UI Unicode symbols with ASCII fallbacks
BOX_TOP = "┌────────────────────────────────────────────────────────┐"
BOX_BOT = "└────────────────────────────────────────────────────────┘"
LINE = "────────────────────────────────────────────────────────"
SPIN_CHARS = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
CHECK_MARK = "✓"
WARN_MARK = "!"

# Check if the terminal encoding supports Unicode box characters
try:
    encoding = sys.stdout.encoding or 'utf-8'
    "┌─┐".encode(encoding)
except Exception:
    # ASCII Fallbacks
    BOX_TOP = "+--------------------------------------------------------+"
    BOX_BOT = "+--------------------------------------------------------+"
    LINE = "--------------------------------------------------------"
    SPIN_CHARS = ['|', '/', '-', '\\']
    CHECK_MARK = "OK"
    WARN_MARK = "!"

URL_PATTERN = re.compile(r'https?://[^\s"\'`<>]+')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    ascii_art = f"""{BOLD}{GREEN}
  _____ _            _____  _                  _             
 |_   _| |__   ___  | ____|___  ___ __ _ _ __ | |_ ___  _ __ 
   | | | '_ \\ / _ \\ |  _| / __|/ __/ _` | '_ \\| __/ _ \\| '__|
   | | | | | |  __/ | |___\\__ \\ (_| (_| | |_) | || (_) | |   
   |_| |_| |_|\\___| |_____|___/\\___\\__,_| .__/ \\__\\___/|_|   
                                        |_|                  {RESET}"""
    print(ascii_art)
    print(f"{BOLD}{CYAN}{BOX_TOP}{RESET}")
    print(f"{BOLD}{CYAN}│{RESET}              {BOLD}Author: {YELLOW}Tengku Arya Saputra{RESET}               {BOLD}{CYAN}│{RESET}")
    print(f"{BOLD}{CYAN}{BOX_BOT}{RESET}")

def clean_endpoint(endpoint):
    """
    Cleans up surrounding quotes, brackets, parentheses, and trailing punctuation recursively.
    """
    endpoint = endpoint.strip()
    
    changed = True
    while changed:
        changed = False
        old_endpoint = endpoint
        endpoint = endpoint.strip()
        
        # Only strip trailing punctuation (no quotes, no backslashes)
        endpoint = endpoint.rstrip('.,;:)"`]>} ')
        # Only strip leading punctuation (no quotes, no backslashes)
        endpoint = endpoint.lstrip('("`[<{ ')
        
        # Strip surrounding quotes (standard and escaped)
        for quote in ['"', "'", '\\"', "\\'"]:
            if endpoint.startswith(quote) and endpoint.endswith(quote):
                ql = len(quote)
                endpoint = endpoint[ql:-ql]
                changed = True
                break
                
        if endpoint != old_endpoint:
            changed = True
            
    return endpoint

def is_js(endpoint):
    """
    Checks if an endpoint is a JavaScript file.
    """
    path_part = endpoint.split('?')[0].split('#')[0]
    return path_part.lower().endswith('.js')

def is_valid_endpoint(cleaned):
    if not cleaned:
        return False
    if '<' in cleaned or '>' in cleaned:
        return False
        
    # An endpoint or path should NEVER contain spaces or whitespace
    if any(c.isspace() for c in cleaned):
        return False
        
    # Limit maximum length of a path to prevent minified JSON blocks from matching
    if len(cleaned) > 250:
        return False
        
    # Split the path part (before query parameters)
    path_part = cleaned.split('?')[0].split('#')[0]
    
    # Path parts should not contain characters from JSON/markup/code
    # E.g. double quotes, commas, backslashes, parentheses, brackets, braces, semicolons, equal signs, ampersands, pipes
    illegal_chars = ['"', "'", ',', '\\', ';', '(', ')', '[', ']', '|', '&', '!', '*', '=', '+']
    if any(char in path_part for char in illegal_chars):
        return False
        
    # Handle curly braces in path_part (only allow matching braces with alphanumeric content like {code})
    if '{' in path_part or '}' in path_part:
        if not re.match(r'^[^{}]*(?:\{[a-zA-Z0-9_]+\}[^{}]*)*$', path_part):
            return False
            
    # Check start indicators
    if cleaned.startswith('//'):
        return len(cleaned) > 2
    elif cleaned.startswith('../'):
        return len(cleaned) > 3
    elif cleaned.startswith('./'):
        return len(cleaned) > 2
    elif cleaned.startswith('/'):
        if ':' in path_part:
            return False
        return len(cleaned) > 1
        
    # If it contains a slash but doesn't start with path indicators
    elif '/' in cleaned:
        # Check if it is a date (e.g. 12/05/2024)
        if re.match(r'^\d{1,4}/\d{1,2}/\d{1,4}$', cleaned):
            return False
        # Check if it is a fraction (e.g. 1/2)
        if re.match(r'^\d+/\d+$', cleaned):
            return False
        if ':' in path_part:
            return False
            
        # Avoid simple word pairs like and/or, yes/no, etc.
        if '.' in cleaned or cleaned.count('/') >= 2:
            return True
        return False
        
    return False

def extract_endpoints_from_text(content):
    """
    Extracts all URLs and paths from text content, safely handling HTML elements.
    """
    endpoints = []
    
    # 1. Extract URLs first
    urls = URL_PATTERN.findall(content)
    for url in urls:
        cleaned_url = clean_endpoint(url)
        if cleaned_url and not ('<' in cleaned_url or '>' in cleaned_url):
            endpoints.append(cleaned_url)
            
    # Remove URLs from content to avoid duplicate matching on path parts of URLs
    temp_content = content
    for url in urls:
        temp_content = temp_content.replace(url, ' ')
        
    # 2. Extract double and single quoted strings (handles escaped quotes)
    double_quotes = re.findall(r'"((?:[^"\\]|\\.)*)"', temp_content)
    for q in double_quotes:
        cleaned = clean_endpoint(q)
        if is_valid_endpoint(cleaned):
            endpoints.append(cleaned)
            
    single_quotes = re.findall(r"'((?:[^'\\]|\\.)*)'", temp_content)
    for q in single_quotes:
        cleaned = clean_endpoint(q)
        if is_valid_endpoint(cleaned):
            endpoints.append(cleaned)
            
    # 3. Strip HTML tags from content to extract plain text paths safely
    stripped_content = re.sub(r'<[^>]*>', ' ', temp_content)
    
    # Split by whitespace and parse tokens
    tokens = stripped_content.split()
    for token in tokens:
        cleaned = clean_endpoint(token)
        if is_valid_endpoint(cleaned):
            endpoints.append(cleaned)
            
    # De-duplicate and preserve order
    seen = set()
    unique_endpoints = []
    for ep in endpoints:
        if ep not in seen:
            seen.add(ep)
            unique_endpoints.append(ep)
            
    return unique_endpoints

def show_spinner(duration=0.8):
    """Shows a micro-spinner to look high-tech and premium."""
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{BOLD}{CYAN}[{SPIN_CHARS[i % len(SPIN_CHARS)]}]{RESET} Memproses data... ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r{BOLD}{GREEN}[{CHECK_MARK}]{RESET} Memproses data... Selesai!\n")
    sys.stdout.flush()

def main():
    while True:
        clear_screen()
        print_header()
        
        print(f" {BOLD}{BLUE}[1]{RESET} URLs Only")
        print(f" {BOLD}{BLUE}[2]{RESET} Paths Only")
        print(f" {BOLD}{BLUE}[3]{RESET} JS Only")
        print(f" {BOLD}{BLUE}[4]{RESET} Keluar (Exit)")
        print(f"{BOLD}{CYAN}{LINE}{RESET}")
        
        try:
            choice = input(f"{BOLD}Pilih Menu [1-4] > {RESET}").strip()
            if choice == '4':
                print(f"\n{BOLD}{GREEN}Terima kasih telah menggunakan TheExtractor! Sampai jumpa.{RESET}\n")
                break
                
            if choice not in ['1', '2', '3']:
                print(f"\n{BOLD}{RED}[{WARN_MARK}] Error: Menu tidak valid. Silakan pilih 1-4.{RESET}")
                time.sleep(1.5)
                continue
                
            filename = input(f"{BOLD}Masukan .txt > {RESET}").strip()
            if not filename:
                print(f"\n{BOLD}{RED}[{WARN_MARK}] Error: Nama file tidak boleh kosong.{RESET}")
                time.sleep(1.5)
                continue
                
            if not os.path.exists(filename):
                print(f"\n{BOLD}{RED}[{WARN_MARK}] Error: File '{filename}' tidak ditemukan.{RESET}")
                time.sleep(2.0)
                continue
                
            # Process file
            print()
            show_spinner(0.6)
            
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            all_endpoints = extract_endpoints_from_text(content)
            
            filtered = []
            menu_name = ""
            
            if choice == '1':
                # URLs Only: starts with http:// or https://
                filtered = [ep for ep in all_endpoints if ep.startswith(('http://', 'https://'))]
                menu_name = "URLs Only"
            elif choice == '2':
                # Paths Only: does NOT start with http:// or https://
                filtered = [ep for ep in all_endpoints if not ep.startswith(('http://', 'https://'))]
                menu_name = "Paths Only"
            elif choice == '3':
                # JS Only: ends with .js (or with query/hashes)
                filtered = [ep for ep in all_endpoints if is_js(ep)]
                menu_name = "JS Only"
                
            print(f"\n{BOLD}{GREEN}─── Hasil Ekstraksi ({menu_name}) ({len(filtered)} item) ───{RESET}")
            if not filtered:
                print(f"{YELLOW}Tidak ada data yang cocok ditemukan.{RESET}")
            else:
                for item in filtered:
                    # Highlight domains or protocols nicely
                    formatted_item = item
                    if item.startswith('https://'):
                        formatted_item = item.replace('https://', f"{DIM}https://{RESET}{BOLD}{GREEN}", 1) + RESET
                    elif item.startswith('http://'):
                        formatted_item = item.replace('http://', f"{DIM}http://{RESET}{BOLD}{GREEN}", 1) + RESET
                    elif item.startswith('./') or item.startswith('../'):
                        formatted_item = f"{BOLD}{YELLOW}{item}{RESET}"
                    else:
                        formatted_item = f"{CYAN}{item}{RESET}"
                        
                    print(formatted_item)
                    
            print(f"{BOLD}{GREEN}{LINE}{RESET}")
            
            # Offer to save results
            if filtered:
                save_choice = input(f"\n{BOLD}{CYAN}[?]{RESET} Apakah Anda ingin menyimpan hasil ke file? (y/n) > ").strip().lower()
                if save_choice in ['y', 'yes']:
                    out_filename = input(f"{BOLD}Masukan Nama File Output > {RESET}").strip()
                    if out_filename:
                        try:
                            with open(out_filename, 'w', encoding='utf-8') as out_f:
                                for item in filtered:
                                    out_f.write(item + '\n')
                            print(f"{BOLD}{GREEN}[{CHECK_MARK}] Hasil berhasil disimpan ke '{out_filename}'!{RESET}")
                        except Exception as e:
                            print(f"{BOLD}{RED}[{WARN_MARK}] Gagal menyimpan file: {e}{RESET}")
                    else:
                        print(f"{BOLD}{YELLOW}[{WARN_MARK}] Nama file kosong, batal menyimpan.{RESET}")
            
            # Ask to continue
            cont_choice = input(f"\n{BOLD}{CYAN}[?]{RESET} Apakah Anda ingin memproses file lain? (y/n) > ").strip().lower()
            if cont_choice not in ['y', 'yes']:
                print(f"\n{BOLD}{GREEN}Terima kasih telah menggunakan TheExtractor! Sampai jumpa.{RESET}\n")
                break
                
        except KeyboardInterrupt:
            print(f"\n\n{BOLD}{YELLOW}Program dibatalkan oleh pengguna.{RESET}\n")
            break
        except Exception as e:
            print(f"\n{BOLD}{RED}[{WARN_MARK}] Terjadi kesalahan: {e}{RESET}")
            time.sleep(3.0)

if __name__ == '__main__':
    main()
