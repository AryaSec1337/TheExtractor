# 🔍 TheExtractor

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/Developer-Tengku%20Arya%20Saputra-orange?style=for-the-badge&logo=github" alt="Developer: Tengku Arya Saputra">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT">
  <img src="https://img.shields.io/badge/Platform-Cross--Platform-lightgrey?style=for-the-badge" alt="Platform">
</p>

`TheExtractor` is a premium, high-performance, and interactive command-line interface (CLI) tool written in Python. It is designed to extract endpoints, pathnames, and URLs from noisy source codes, minified scripts, log files, or raw HTML/HTTP dump files.

---

## ✨ Core Features

*   🚀 **Intelligent Filtering & Cleaning**:
    *   **HTML Tag Stripper**: Automatically strips HTML elements, preventing closing tags (like `</ol>`, `</li>`, `</span>`) from registering as false-positive paths.
    *   **JS/JSON Code Ignorer**: Smarts-filter to ignore minified JS code fragments, logic statements, fractions, dates, and base64 strings.
    *   **Recursive Quote Stripping**: Safely unpacks standard and escaped double/single quotes (`\"` and `\'`) from attributes, JSON keys, and strings.
*   🎯 **Three Extraction Modes**:
    1.  **URLs Only**: Extracts complete HTTP/HTTPS links.
    2.  **Paths Only**: Extracts clean relative and absolute pathnames (e.g. `/api/v1/users`, `./styles.css`).
    3.  **JS Only**: Extracts only JavaScript file endpoints (ending in `.js`).
*   🎨 **Premium UI/UX Console**:
    *   Sleek ASCII Art Title Banner.
    *   Color-coded list rendering with custom highlights for protocols and paths.
    *   Micro-spinner processing animation.
    *   Automatic fallback to clean ASCII borders on legacy terminal configurations (preventing `UnicodeEncodeError`).
*   💾 **Interactive File Export**: Instantly save your extraction results to a file at the end of the run.
*   🔄 **Interactive Session Loop**: Process multiple files sequentially without having to restart the script.

---

## 🖥️ Preview & Visual Design

When running the application, you will be greeted by a premium-styled terminal layout:

```text
  _____ _            _____  _                  _             
 |_   _| |__   ___  | ____|___  ___ __ _ _ __ | |_ ___  _ __ 
   | | | '_ \ / _ \ |  _| / __|/ __/ _` | '_ \| __/ _ \| '__|
   | | | | | |  __/ | |___\__ \ (_| (_| | |_) | || (_) | |   
   |_| |_| |_|\___| |_____|___/\___\__,_| .__/ \__\___/|_|   
                                        |_|                  
┌────────────────────────────────────────────────────────┐
│              Author: Tengku Arya Saputra               │
└────────────────────────────────────────────────────────┘
 [1] URLs Only
 [2] Paths Only
 [3] JS Only
 [4] Keluar (Exit)
────────────────────────────────────────────────────────
Pilih Menu [1-4] > 2
Masukan .txt > request.txt

[✓] Memproses data... Selesai!

─── Hasil Ekstraksi (Paths Only) (3 item) ───
/info/privacy.html#cookies
/api/cronos/mkt/UpdateConsentConfiguration
./coinbase/styles.scss
────────────────────────────────────────────────────────

[?] Apakah Anda ingin menyimpan hasil ke file? (y/n) > y
Masukan Nama File Output > output_paths.txt
[✓] Hasil berhasil disimpan ke 'output_paths.txt'!

[?] Apakah Anda ingin memproses file lain? (y/n) > n
Terima kasih telah menggunakan TheExtractor! Sampai jumpa.
```

---

## 🚀 Quick Start

### 1. Requirements
*   Python **3.7 or higher**
*   Zero external dependencies (runs out-of-the-box on standard Python installs)

### 2. Installation
Clone this repository to your local system:
```bash
git clone https://github.com/AryaSec1337/TheExtractor.git
cd TheExtractor
```

### 3. Usage
Run the main script:
```bash
python TheExtractor.py
```

---

## ⚙️ How It Works (Under the Hood)

1.  **URL Isolation**: The tool sweeps the file first for absolute HTTP/HTTPS links, isolating them to prevent path duplicate hits.
2.  **Attribute & String Scan**: Scans all double and single-quoted strings using recursive quote cleaning, extracting paths inside HTML/JSX attributes or JS keys (e.g. `href="/api"`).
3.  **HTML/Tag Cleanup**: Strips remaining XML/HTML markup tag blocks, then splits the remaining text by whitespace to parse final tokens.
4.  **Syntax Verification**: Validates each endpoint candidate through a checklist of illegal characters (like `=, ;, |, &, !, [, ]`) to drop code fragments.

---

## 🧑‍💻 Author

*   **Tengku Arya Saputra**
*   GitHub: [@AryaSec1337](https://github.com/AryaSec1337)

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
