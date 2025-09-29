# Favicon and Icon Assets

Since we've updated the HTML to reference local favicon files, you'll need to add these assets to your `public` directory:

## Required Files:
- `public/favicon.ico` - Standard favicon (16x16, 32x32, 48x48 sizes)
- `public/apple-touch-icon.png` - Apple touch icon (180x180)
- `public/og-image.png` - Open Graph image for social media (1200x630)

## Quick Setup:

You can create these from the SVG logo I generated at `public/lasomi-logo.svg`:

1. **Convert SVG to ICO**: Use an online converter to create `favicon.ico`
2. **Create PNG versions**: Export the SVG as PNG at required sizes
3. **Social media image**: Create a 1200x630 banner with your logo and tagline

## Temporary Solution:
The build works fine without these files - browsers will just use default icons until you add proper assets.

For now, the SVG favicon at `public/favicon.svg` will work in modern browsers.