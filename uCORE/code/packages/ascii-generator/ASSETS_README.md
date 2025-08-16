# ASCII Generator Assets

This directory contains demo assets and fonts for the ASCII Generator.

## Structure
- `demo/` - Demo images and outputs (not included in repository)
- `data/` - Input data files (not included in repository) 
- `fonts/` - TrueType fonts (not included in repository)

## Download Assets
These assets are large and not included in the git repository. 
They will be downloaded automatically when needed or can be added manually:

```bash
# Download from original repository if needed
cd uCode/packages/ascii-generator
git clone https://github.com/vietnh1009/ASCII-generator.git temp-download
cp -r temp-download/demo ./
cp -r temp-download/data ./
cp -r temp-download/fonts ./
rm -rf temp-download
```

## Fonts
The ASCII generator will work with system fonts. For enhanced output:
- DejaVu Sans Mono (monospace)
- Arial Unicode (wide character support)
- System default monospace font

## Demo Content
Demo files include:
- Sample images (.jpg, .png, .gif)
- Generated ASCII art examples
- Video conversion examples

These are optional and only needed for testing/examples.
