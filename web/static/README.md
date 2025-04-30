# FaceAuth - Static Assets

## Overview

This directory contains **static frontend resources** used by the FaceAuth web interface.

Currently, it includes global CSS styles applied across all HTML pages in the system.

---

## Files

### `style.css`
Defines the core visual styling for the platform.

### Key Elements Styled:

- `body`:  
  Sets the global font to Arial, centers content, and applies a light gray background.

- `.container`:  
  Used for centering content blocks such as login and registration boxes.  
  It applies padding, white background, rounded corners, and soft box shadow.

- `.btn`:  
  Reusable button style for navigation and actions.  
  Styled with padding, blue background, white text, and hover effect.

---

## Visual Identity

The style is kept **minimal and clean** to ensure:

- Consistency across all views (login, dashboard, user area).
- Good readability and focus on functionality.
- Smooth visual experience across devices.

---

## Note

This CSS is loaded in all HTML templates using:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
