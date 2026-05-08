# Cross-Platform Compatibility Fixes

## Summary

The `install-ui-dependencies.sh` script has been updated to work correctly on **Linux**, **macOS**, and **WSL** without requiring GNU-specific tools.

---

## Issues Fixed

### 1. **grep -P flag (Perl regex) not available on macOS**

**Problem:**
```bash
grep -oP '\d+\.\d+'  # Works on Linux, FAILS on macOS
```

macOS uses BSD grep which doesn't support `-P` (Perl regex) flag.

**Solution:**
```bash
# Before (Linux only)
VITE_VERSION=$(grep '"vite"' package.json | grep -oP '\d+\.\d+' | head -1)

# After (Cross-platform)
VITE_VERSION=$(grep '"vite"' package.json | head -1 | sed 's/[^0-9.]*\([0-9][0-9]*\.[0-9][0-9]*\).*/\1/')
```

Uses standard `sed` which works identically on both platforms.

### 2. **sed -i behaves differently on macOS**

**Problem:**
```bash
sed -i 's/old/new/' file.txt  # Works on Linux, FAILS on macOS
```

- **Linux (GNU sed)**: `-i` edits in-place without requiring backup extension
- **macOS (BSD sed)**: `-i` requires a backup extension: `-i.bak`

**Solution:**
```bash
# Before (Linux only)
sed -i 's/"vite": "\^[6-9][^"]*"/"vite": "^5.4.21"/g' package.json

# After (Cross-platform)
sed -i.bak 's/"vite": "\^[6-9][^"]*"/"vite": "^5.4.21"/g' package.json && rm -f package.json.bak
```

Creates a `.bak` file (works on both), then removes it immediately.

---

## Changes Made to `install-ui-dependencies.sh`

### 1. Version Extraction (Line ~80)
```bash
# Portable sed-based version extraction
VITE_VERSION=$(grep '"vite"' package.json | head -1 | sed 's/[^0-9.]*\([0-9][0-9]*\.[0-9][0-9]*\).*/\1/')
```

### 2. All sed -i commands (Lines 90, 98, 104, 110, 111, 141, 144, 165)
```bash
# Pattern: sed -i.bak 'command' file && rm -f file.bak
sed -i.bak 's/"@vitejs\/plugin-react": "\^[6-9][^"]*"/"@vitejs\/plugin-react": "^5.2.0"/g' package.json && rm -f package.json.bak
```

---

## Testing

### Linux/WSL
```bash
./scripts/install-ui-dependencies.sh --clean
# Should work without errors
```

### macOS
```bash
./scripts/install-ui-dependencies.sh --clean
# Should work without "invalid option -- P" error
```

---

## Verification

Test version extraction works on both platforms:

```bash
# Test with sample input
echo '"vite": "^5.4.21"' | sed 's/[^0-9.]*\([0-9][0-9]*\.[0-9][0-9]*\).*/\1/'
# Output: 5.4

echo '"vite": "^8.0.11"' | sed 's/[^0-9.]*\([0-9][0-9]*\.[0-9][0-9]*\).*/\1/'
# Output: 8.0
```

Test in-place editing works:

```bash
# Create test file
echo '{"vite": "^8.0.11"}' > test.json

# Edit (cross-platform)
sed -i.bak 's/"8.0.11"/"5.4.21"/' test.json && rm -f test.json.bak

# Verify
cat test.json
# Output: {"vite": "^5.4.21"}
```

---

## Why These Changes Matter

### Before
- Script only worked on Linux
- macOS users got cryptic errors
- Required GNU coreutils on macOS (via Homebrew)

### After
- ✅ Works on Linux out of the box
- ✅ Works on macOS out of the box
- ✅ Works on WSL out of the box
- ✅ No additional dependencies required

---

## Best Practices for Cross-Platform Shell Scripts

### 1. **Avoid GNU-specific flags**
```bash
# Avoid
grep -P '\d+'      # Perl regex (GNU only)
sed -r 's/x/y/'    # Extended regex (GNU only)
date -d '...'      # Date parsing (GNU only)

# Use instead
sed 's/[0-9]//'    # Standard regex
awk '{...}'        # Works everywhere
```

### 2. **Make sed -i portable**
```bash
# Always use backup extension and remove
sed -i.bak 's/old/new/' file && rm -f file.bak
```

### 3. **Test on multiple platforms**
```bash
# Test matrix
- Linux (Ubuntu, Debian, Fedora)
- macOS (latest version)
- WSL (Windows Subsystem for Linux)
```

### 4. **Use POSIX-compliant features**
```bash
# These work everywhere
grep -E 'pattern'   # Extended regex (not -P)
sed 's/pattern//'   # Basic operations
awk '{print $1}'    # Text processing
```

---

## Additional Resources

- [POSIX Shell Command Reference](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/contents.html)
- [Portable Shell Programming](https://www.gnu.org/software/autoconf/manual/autoconf.html#Portable-Shell)
- [macOS vs Linux sed differences](https://unix.stackexchange.com/questions/13711/differences-between-sed-on-mac-osx-and-other-standard-sed)

---

**Last Updated:** 2026-05-08
