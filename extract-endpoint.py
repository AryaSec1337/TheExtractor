#!/usr/bin/env python3
import sys
import os
import re
import argparse

# Regex for matching HTTP/HTTPS URLs
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

def extract_endpoints(content):
    """
    Extracts URLs and path-like endpoints from content.
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
            # Check if it is a date (e.g., 12/05/2024 or 2024/05/12)
            if re.match(r'^\d{1,4}/\d{1,2}/\d{1,4}$', cleaned):
                continue
            # Check if it is a fraction (e.g., 1/2)
            if re.match(r'^\d+/\d+$', cleaned):
                continue
            # Otherwise, if it contains a slash and is not a date/fraction, consider it an endpoint
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
    parser = argparse.ArgumentParser(description="Extract endpoints and URLs from a text file.")
    parser.add_argument('-l', '--list', dest='input_file', help="Path to the input text file. Use '-' or omit to read from stdin.")
    parser.add_argument('-o', '--output', dest='output_file', help="Path to save the extracted endpoints.")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress status and statistics messages on stderr.")
    
    args = parser.parse_args()
    
    content = ""
    # Read input
    if args.input_file and args.input_file != '-':
        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.input_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Check if stdin is tty (interactive) or piped
        if sys.stdin.isatty():
            if not args.quiet:
                print("Reading from stdin... Press Ctrl+D (Ctrl+Z on Windows) to end input.", file=sys.stderr)
        content = sys.stdin.read()
        
    # Extract
    endpoints = extract_endpoints(content)
    
    # Write to output file if specified
    if args.output_file:
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                for ep in endpoints:
                    f.write(ep + '\n')
            if not args.quiet:
                print(f"[+] Successfully extracted {len(endpoints)} unique endpoints and saved to '{args.output_file}'.", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print to stdout
        for ep in endpoints:
            print(ep)
        if not args.quiet:
            print(f"\n[+] Total unique endpoints found: {len(endpoints)}", file=sys.stderr)

if __name__ == '__main__':
    main()
