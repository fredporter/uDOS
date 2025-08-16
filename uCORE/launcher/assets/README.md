# uDOS Launcher Assets

This directory contains visual assets for the uDOS launcher system:

## Icons
- `udos-icon.png` - Main uDOS application icon (256x256)
- `udos-icon.ico` - Windows ICO format
- `udos-icon.icns` - macOS ICNS format

## Platform Assets
- Platform-specific launcher icons
- Application bundle resources
- Desktop integration assets

## Creating Icons

To create proper icons from a source image:

### macOS (.icns)
```bash
# Create iconset directory
mkdir uDOS.iconset

# Generate different sizes
sips -z 16 16 source.png --out uDOS.iconset/icon_16x16.png
sips -z 32 32 source.png --out uDOS.iconset/icon_16x16@2x.png
sips -z 32 32 source.png --out uDOS.iconset/icon_32x32.png
sips -z 64 64 source.png --out uDOS.iconset/icon_32x32@2x.png
sips -z 128 128 source.png --out uDOS.iconset/icon_128x128.png
sips -z 256 256 source.png --out uDOS.iconset/icon_128x128@2x.png
sips -z 256 256 source.png --out uDOS.iconset/icon_256x256.png
sips -z 512 512 source.png --out uDOS.iconset/icon_256x256@2x.png
sips -z 512 512 source.png --out uDOS.iconset/icon_512x512.png
sips -z 1024 1024 source.png --out uDOS.iconset/icon_512x512@2x.png

# Create ICNS file
iconutil -c icns uDOS.iconset
```

### Windows (.ico)
```bash
# Using ImageMagick
convert source.png -resize 256x256 -colors 256 udos-icon.ico
```

### Linux (.png)
Standard PNG icons work for most Linux desktop environments. Recommended sizes:
- 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
