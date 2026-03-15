# Smart Image Generator

🎨 An intelligent AI-powered image generation skill for OpenClaw with multi-step interaction, smart style recommendations, and comprehensive parameter configuration.

## Features

- **Dual Generation Modes**: Text-to-Image and Image-to-Image support
- **38 Art Styles**: Extensive style library with intelligent recommendations
- **14 Basic Parameters**: Aspect ratio, shot size, camera angle, composition, and more
- **134 Advanced Parameters**: Optics, lighting, color tone, materials, and style-specific settings
- **Smart Negative Prompts**: Automatically style-aware negative prompt recommendations
- **One-Click Configuration**: Streamlined workflow with intelligent defaults
- **Multi-Step Interaction**: Guided process ensuring quality results

## Installation

```bash
clawhub install smart-image-generator
```

Or manually clone this repository into your OpenClaw workspace skills directory.

## Usage

Simply express your image generation needs in natural language:

```
Generate an image of a girl dancing
```

The skill will guide you through:

1. **Mode Selection**: Choose Text-to-Image or Image-to-Image
2. **Style Recommendation**: 3-5 intelligently recommended styles from 38 options
3. **Parameter Configuration**: 14 basic parameters with explanations
4. **Advanced Options** (optional): 134 advanced parameters for fine-tuning
5. **Negative Prompts** (optional): Smart style-aware exclusions
6. **Image Generation**: High-quality output using AI native capabilities
7. **Review**: Complete configuration summary

## Supported Art Styles (38)

- **Traditional**: Sketch, Freehand, Impressionism, Post-Impressionism, Fine Brush, Woodcut
- **Classical**: Baroque, Renaissance, Romanticism
- **Watercolor**: Wet Watercolor, English Transparent Watercolor
- **Modern**: Expressionism, Art Deco, Surrealism, Pop Art, Minimalism
- **Illustration**: European Picture Book, Toon Render, Flat Illustration, Texture Illustration
- **Digital**: Concept Art, Korean Semi-Thick Paint, Realistic 3D Render
- **Futuristic**: Sci-Fi Mechanical, Vaporwave, Cyberpunk, Retrofuturism/Y3K
- **Stylized**: Miyazaki Style, Ugly/Cute, Imperfection/Handmade, Chicken Claw Style
- **Avant-Garde**: Alternative Historical, Dopamine Color/Supercolor, Floating Light Dream, Avant-Garde China Style

## Basic Parameters (14)

1. **Aspect Ratio**: 1:1, 3:4, 16:9, 2.35:1
2. **Shot Size**: Close-up, Medium Shot, Medium Long Shot, Long Shot
3. **Camera Angle**: Eye Level, High Angle, Low Angle, Worm's-eye
4. **Perspective Type**: Flat, One-Point, Two-Point, Three-Point, Scattered, Fisheye, Aerial
5. **Composition**: Center, Rule of Thirds, Golden Ratio, Diagonal, Frame, Symmetrical, Leading Lines, S-Curve
6. **Color Tone**: Warm, Cool, Neutral, Black & White
7. **Exposure**: High Key, Mid Key, Low Key
8. **Lighting**: Front Light, Side Light, Back Light, Soft Light, Hard Light, Natural Light
9. **Saturation**: Low, Standard, High
10. **Texture Strength**: Weak, Medium, Strong
11. **Contrast**: Low, Medium, High
12. **Edge Sharpening**: Weak, Medium, Strong
13. **Color Space**: sRGB, Adobe RGB, ProPhoto RGB, DCI-P3
14. **Depth of Field Control**: Shallow, Medium, Deep

## Advanced Parameters (134)

Comprehensive parameter categories:

- **Optics & Lens** (7 items): Focal length, aperture, lens type, depth of field, etc.
- **Lighting** (12 items): Light source, intensity, color temperature, shadow quality, etc.
- **Color & Tone** (15 items): Color palette, contrast, saturation, vibrance, hue shift, etc.
- **Composition & Visual** (20 items): Balance, harmony, visual flow, focal points, etc.
- **Material & Style** (25 items): Texture, surface quality, material properties, style attributes, etc.
- **Technical Quality** (15 items): Resolution, sharpness, noise reduction, detail enhancement, etc.
- **Atmosphere & Mood** (12 items): Emotional tone, atmosphere, lighting mood, color psychology, etc.
- **Artistic Effects** (18 items): Brush strokes, rendering style, artistic techniques, texture overlays, etc.
- **Post-Processing** (10 items): Color grading, vignette, film grain, lens effects, etc.

## Workflow Example

```
User: Generate an image of a girl dancing

Smart Image Generator: Please select generation mode:
1. Text-to-Image
2. Image-to-Image

User: 1

Smart Image Generator: Please describe the image content you want to generate.

User: A girl dancing in a modern dance studio

Smart Image Generator: Based on your description, I recommend these styles:
A. ★ Realism - Best for capturing natural movements and lighting
B. Concept Art - Great for dynamic poses and atmospheric lighting
C. Minimalism - Clean and focused on the subject
...

User: A

Smart Image Generator: Here are the recommended parameters for Realism style:
- Aspect Ratio: 16:9 (Widescreen shows the studio space)
- Shot Size: Medium Shot (Balances dancer and environment)
- Camera Angle: Eye Level (Natural perspective)
...

User: Use these configurations to generate image

[Image generated]

Smart Image Generator: ✨ Generation Review
📝 Your description: A girl dancing in a modern dance studio
🎨 Selected style: Realism
⚙️ Configuration: [Complete parameter list]
🖼️ Generated image: [Display image]
```

## Requirements

- OpenClaw with native AI image generation capabilities
- No additional credentials or API keys required

## Technical Details

- Uses AI native image generation (no external scripts)
- Supports JPEG, PNG, WEBP formats for Image-to-Image
- Style library with 38 predefined styles
- Smart parameter recommendations based on selected style
- Comprehensive negative prompt management

## License

MIT License - Feel free to use and modify for your needs.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Support

For issues or questions, please open an issue on the repository.

---

**🐱 Smart Image Generator - Happy Creating! 🐱**
