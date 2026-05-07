# Shared Assets

This directory contains shared assets used across multiple portals (Customer, Adjustor, Admin, etc.).

## ACME-logo.png

**Company:** ACME Insurance  
**Usage:** Display in all portal headers and login pages  
**Original Location:** Copied from `/mnt/c/Users/raj/Downloads/ACME-log.png`

### Usage Guidelines

**Customer Portal:**
- Header: Top-left corner, ~120-150px width
- Login Page: Centered, ~80-100px width
- Link to home page (`/`)

**Adjustor Portal:**
- Header: Top-left corner, ~120px width, inverted colors for dark background
- Login Page: Centered, ~80-100px width
- Link to dashboard page (`/dashboard`)

**Admin Portal (Future):**
- Similar placement to Adjustor Portal

### Technical Details

- **Format:** PNG
- **Size:** 2.1 MB
- **Color Mode:** RGB (can be inverted via CSS for dark backgrounds)
- **Transparency:** Check if logo has transparent background
- **Aspect Ratio:** Maintain original aspect ratio when resizing

### Accessing from Portals

**From Customer Portal:**
```jsx
<img src="/src/common/assets/ACME-logo.png" alt="ACME Insurance" />
```

**From Adjustor Portal:**
```jsx
<img src="/src/common/assets/ACME-logo.png" alt="ACME Insurance" className="brightness-0 invert" />
```

**Note:** Adjust paths based on build configuration and deployment structure.

### Updating the Logo

If the logo needs to be updated:
1. Replace `ACME-logo.png` in this directory
2. Clear browser cache in all portals
3. Rebuild production bundles
4. Test visibility on both light and dark backgrounds
5. Update this README if usage guidelines change
