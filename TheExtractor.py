#!/usr/bin/env python3
import sys
import os
import re

# Colors for terminal styling
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

URL_PATTERN = re.compile(r'https?://[^\s"\'`<>]+')

def clean_endpoint(endpoint):
    """
    Cleans up surrounding quotes, brackets, parentheses, and trailing punctuation.
    """
    endpoint = endpoint.strip()
    
    # Strip matched surrounding brackets/quotes
    changed = True
    while changed:
        changed = False
        if len(endpoint) >= 2:
            if (endpoint[0] == '"' and endpoint[-1] == '"') or (endpoint[0] == "'" and endpoint[-1] == "'"):
                endpoint = endpoint[1:-1]
                changed = True
            elif endpoint[0] == '(' and endpoint[-1] == ')':
                endpoint = endpoint[1:-1]
                changed = True
            elif endpoint[0] == '[' and endpoint[-1] == ']':
                endpoint = endpoint[1:-1]
                changed = True
            elif endpoint[0] == '{' and endpoint[-1] == '}':
                endpoint = endpoint[1:-1]
                changed = True
                
    # Strip trailing punctuation (but not letters, numbers, slashes, or valid query params)
    endpoint = endpoint.rstrip('.,;:)"`]>} ')
    # Strip leading punctuation/brackets (but NOT dots or slashes!)
    endpoint = endpoint.lstrip('("`[<{ ')
    
    return endpoint

def is_js(endpoint):
    """
    Checks if an endpoint is a JavaScript file.
    """
    path_part = endpoint.split('?')[0].split('#')[0]
    return path_part.lower().endswith('.js')

def extract_endpoints_from_text(content):
    """
    Extracts all URLs and paths from text content.
    """
    endpoints = []
    
    # 1. Extract URLs
    urls = URL_PATTERN.findall(content)
    for url in urls:
        cleaned_url = clean_endpoint(url)
        if cleaned_url:
            endpoints.append(cleaned_url)
            
    # Remove URLs from text to avoid duplicate matching on path parts of URLs
    temp_text = content
    for url in urls:
        temp_text = temp_text.replace(url, ' ')
        
    # 2. Extract path-like structures
    tokens = temp_text.split()
    for token in tokens:
        cleaned = clean_endpoint(token)
        if not cleaned:
            continue
            
        # Check if it looks like an endpoint
        if cleaned.startswith('/') or cleaned.startswith('./') or cleaned.startswith('../'):
            if len(cleaned) > 1:  # avoid single "/"
                endpoints.append(cleaned)
        elif '/' in cleaned:
            # Check if it is a date (e.g. 12/05/2024)
            if re.match(r'^\d{1,4}/\d{1,2}/\d{1,4}$', cleaned):
                continue
            # Check if it is a fraction (e.g. 1/2)
            if re.match(r'^\d+/\d+$', cleaned):
                continue
            # Otherwise, if it has a slash and is not a date/fraction, it might be a path
            endpoints.append(cleaned)
            
    # De-duplicate and preserve order
    seen = set()
    unique_endpoints = []
    for ep in endpoints:
        if ep not in seen:
            seen.add(ep)
            unique_endpoints.append(ep)
            
    return unique_endpoints

def main():
    print(f"\n{BOLD}{BLUE}======================================{RESET}")
    print(f"{BOLD}{GREEN}             TheExtractor             {RESET}")
    print(f"{BOLD}{BLUE}======================================{RESET}")
    print("1. Extract Endpoints")
    print("2. Extract JS")
    print("3. Extract URLs")
    print(f"{BOLD}{BLUE}======================================{RESET}")
    
    try:
        # Prompt Menu
        choice = input(f"{BOLD}Pilih Menu > {RESET}").strip()
        if choice not in ['1', '2', '3']:
            print(f"{RED}Error: Menu tidak valid.{RESET}")
            return
            
        # Prompt File
        filename = input(f"{BOLD}Masukan .txt > {RESET}").strip()
        if not filename:
            print(f"{RED}Error: Nama file tidak boleh kosong.{RESET}")
            return
            
        if not os.path.exists(filename):
            print(f"{RED}Error: File '{filename}' tidak ditemukan.{RESET}")
            return
            
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        all_endpoints = extract_endpoints_from_text(content)
        
        filtered = []
        menu_name = ""
        
        if choice == '1':
            filtered = all_endpoints
            menu_name = "Endpoints"
        elif choice == '2':
            filtered = [ep for ep in all_endpoints if is_js(ep)]
            menu_name = "JS Files"
        elif choice == '3':
            filtered = [ep for ep in all_endpoints if ep.startswith(('http://', 'https://'))]
            menu_name = "URLs"
            
        print(f"\n{BOLD}{GREEN}--- Hasil Ekstraksi ({menu_name}) ---{RESET}")
        if not filtered:
            print(f"{YELLOW}Tidak ada data yang cocok ditemukan.{RESET}")
        else:
            for item in filtered:
                print(item)
            print(f"\n{BOLD}{GREEN}[+] Berhasil mengekstrak {len(filtered)} item.{RESET}")
            
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Program dibatalkan oleh pengguna.{RESET}")
    except Exception as e:
        print(f"\n{RED}Terjadi kesalahan: {e}{RESET}")

if __name__ == '__main__':
    main()
