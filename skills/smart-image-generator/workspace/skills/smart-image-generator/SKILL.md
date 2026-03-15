---
name: smart-image-generator
description: Smart Image Generator. When users say "generate image", "create picture", "draw XX", "I want XX image", "use smart image generator skill", "smart-image-generator", or any expression indicating image generation intent, immediately trigger this Skill. Through multi-step interaction flow, recommends 3-5 styles (with reasons), configures 14 basic parameters and 134 advanced parameters, uses AI native capabilities to generate high-quality images. Supports both text-to-image and image-to-image modes with strict multi-step flow, one-click smart parameter configuration, ready to use out of the box.
metadata: { "openclaw": { "emoji": "🎨" } }
---

# Smart Image Generator

## 🎯 Trigger Conditions (Must Trigger Skill Immediately)

**When users express any of the following intents, you must immediately use this Skill:**

- ✅ Direct requests: "generate image", "create picture", "I want an image", "help me draw XX"
- ✅ Explicit specification: "use smart image generator skill", "use smart-image-generator", "call image generation skill"
- ✅ Expression of needs: "I want to generate an image of XX scene", "draw an image in XX style", "convert this image to XX style"
- ✅ Any other natural language expressing image generation intent

**⚠️⚠️⚠️ After triggering, immediately execute Step 1. Never respond in a generic way! ⚠️⚠️⚠️**

**❌ Wrong Trigger Example:**
User: "Smart image generator skill, I want to generate an image"
❌ AI: "Received, I'll help you generate an image. But to generate an image that better matches your expectations, I need you to tell me the following information..." ← This is wrong!

**✅ Correct Trigger Example:**
User: "Smart image generator skill, I want to generate an image"
✅ AI: "Please select generation mode: 1. Text-to-Image 2. Image-to-Image" ← This is correct!

---

## ⛔⛔⛔ Highest Priority Warning (Must Read First) ⛔⛔⛔

🚨🚨🚨 **Strictly Forbidden to Generate Images Directly!** 🚨🚨🚨

Even if users say "generate an image of XX", "I want an XX picture", "help me draw XX", you absolutely must not generate directly!

**Must follow this flow:**
1. Ask for generation mode (text-to-image/image-to-image)
2. Recommend 3-5 styles (with reasons)
3. Recommend 14 basic parameters (with reasons)
4. User confirms configuration
5. Generate 1 image (only 1 image)
6. Show generation review

❌ Wrong example:
User: "Generate an image of a girl dancing"
❌ AI: [Directly generates image] ← This is wrong!

✅ Correct behavior:
User: "Generate an image of a girl dancing"
✅ AI: Please select generation mode: 1. Text-to-Image 2. Image-to-Image

⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔⛔

---

## Task Objective
- This Skill is used to: Based on user's natural language description, intelligently recommend art styles and configure parameters, using AI native capabilities to generate high-quality images
- Capabilities include: text-to-image (AI native), image-to-image (AI native), 38 art style recommendations, 14 basic parameter configurations, 134 advanced parameter configurations
- Trigger conditions: User requests image generation, create artwork based on description, convert image to specific art style

## Prerequisites
- No special prerequisites required
- Image generation depends on AI native image generation capabilities
- No additional credential configuration needed

## 🚨 Pre-Generation Checklist (Must check before generating any image)

Before generating any image, confirm the following steps are completed:

- [ ] Step 1: Asked user for generation mode (text-to-image/image-to-image) and received user's choice
- [ ] Step 2: Obtained user description or reference image
- [ ] Step 3: Recommended 3-5 styles from 38 styles, each with recommendation reason
- [ ] Step 4: Waited for user to select a style
- [ ] Step 5: Recommended 14 basic parameters, each with recommendation reason
- [ ] Step 6 (Optional): If user chooses advanced parameters, recommended and waited for user confirmation
- [ ] Step 7: Displayed complete configuration and waited for user to confirm generation

**⚠️⚠️⚠️ If any item above is not completed, image generation is strictly forbidden! ⚠️⚠️⚠️**

---

## Operation Steps

🚨🚨🚨 All steps below must be executed in strict order. Wait for user confirmation after completing each step before proceeding to the next! 🚨🚨🚨

⚠️⚠️⚠️ Absolutely forbidden: Skip steps to generate images directly! ⚠️⚠️⚠️

⚠️⚠️⚠️ Absolutely forbidden: Display all steps at once for user to select! ⚠️⚠️⚠️

⚠️⚠️⚠️ Must guide step by step: Step 1 → User confirm → Step 2 → User confirm → Step 3... ⚠️⚠️⚠️

---

### Step 1: Determine Generation Mode

**⚠️⚠️⚠️ Do not skip this step! Must wait for user to select! ⚠️⚠️⚠️**

Ask user:
```
Please select generation mode:
1. Text-to-Image - Generate images through text description
2. Image-to-Image - Generate new images based on reference image (editing, style conversion)
```

---

### Step 2: Get Description or Reference Image

**⚠️⚠️⚠️ Do not skip this step! Must get description or reference image! ⚠️⚠️⚠️**

**If user selects "Text-to-Image":**
Ask: "Please describe the image content you want to generate."

**If user selects "Image-to-Image":**
1. **⚠️⚠️⚠️ Must wait for user to upload reference image! ⚠️⚠️⚠️**
   - Ask: "Please upload a reference image, or provide an image URL."
   - Supported formats: JPG, PNG, WEBP, etc.
   - Can upload image directly in conversation
2. **⚠️⚠️⚠️ Must use user-uploaded reference image! ⚠️⚠️⚠️**
   - Absolutely cannot ignore user-uploaded reference image
   - Must reference original image's character features, facial features, expressions, etc.
3. Ask: "Please tell me how you want to process this reference image?"
   - Keep character features / Change scene / Adjust expression / Add elements, etc.

**⚠️⚠️⚠️ Image-to-Image must use user-uploaded reference image! Absolutely cannot ignore! ⚠️⚠️⚠️**

---

### Step 3: Recommend Art Styles

**⚠️⚠️⚠️ Do not skip this step! Must recommend 3-5 styles, each with recommendation reason! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Must read complete 38 styles list from style-library.md! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Forbidden to use built-in list! Must list all 38 styles for user to choose from! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Forbidden to auto-select style! Must wait for user to select! ⚠️⚠️⚠️**

Read complete 38 styles from [references/style-library.md](references/style-library.md) and execute:

```
🎨 Based on your description, I recommend the following art styles (selected from 38 styles):

A. ★ [Style Name] - Recommendation reason: [Explain why it matches]
B. [Style Name] - Recommendation reason: [Explain]
C. [Style Name] - Recommendation reason: [Explain]
D. [Style Name] - Recommendation reason: [Explain]
E. [Style Name] - Recommendation reason: [Explain]

💡 You can choose the recommended styles above (A/B/C/D/E), or select from the 38 styles below:

1. Sketch 2. Freehand 3. Impressionism 4. Post-Impressionism 5. Aesthetic Ancient Style
6. Fine Brush 7. Baroque 8. Renaissance 9. Dark Fantasy 10. Woodcut
11. European Picture Book 12. Romanticism 13. Wet Watercolor 14. Realism 15. English Transparent Watercolor
16. Expressionism 17. Art Deco 18. Surrealism 19. Toon Render 20. Flat Illustration
21. Minimalism 22. Concept Art 23. Pop Art 24. Texture Illustration 25. Korean Semi-Thick Paint
26. Realistic 3D Render 27. Sci-Fi Mechanical 28. Vaporwave 29. Cyberpunk 30. Miyazaki Style
31. Ugly/Cute 32. Imperfection/Handmade 33. Chicken Claw Style 34. Retrofuturism/Y3K Aesthetic
35. Alternative Historical 36. Dopamine Color/Supercolor 37. Floating Light Dream 38. Avant-Garde China Style
```

**⚠️ Forbidden to auto-select style! Must wait for user to select! ⚠️⚠️⚠️**

**⚠️ Absolutely forbidden: After recommending styles, directly go to parameter recommendations without waiting for user to select! ⚠️⚠️⚠️**

---

### Step 4: Wait for User to Select Style

**⚠️⚠️⚠️ Do not skip this step! Must wait for user to select style! ⚠�⚠️⚠️**

**⚠️⚠️⚠️ Forbidden to auto-select "Realism Style" or any other style! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Forbidden to recommend parameters directly after recommending styles without waiting for user to select! ⚠️⚠️⚠️**

Wait for user to input style name.

---

### Step 5: Recommend Basic Parameters

**⚠️⚠️⚠️ Do not skip this step! Must recommend 14 basic parameters, each with recommendation reason! ⚠️⚠️⚠️**

Based on the style user selected, extract corresponding 14 basic parameter configurations from the style library and display to user.

**14 Basic Parameters List:**
1. Aspect Ratio (1:1/3:4/16:9/2.35:1)
2. Shot Size (Close-up/Medium Shot/Medium Long Shot/Long Shot)
3. Camera Angle (Eye Level/High Angle/Low Angle/Worm's-eye)
4. Perspective Type (Flat Perspective/One-Point Perspective/Two-Point Perspective/Three-Point Perspective/Scattered Perspective/Fisheye Perspective/Aerial Perspective)
5. Composition (Center Composition/Rule of Thirds/Golden Ratio/Diagonal Composition/Frame Composition/Symmetrical Composition/Leading Lines/S-Curve)
6. Color Tone (Warm Tone/Cool Tone/Neutral Tone/Black & White)
7. Exposure (High Key/Mid Key/Low Key)
8. Lighting (Front Light/Side Light/Back Light/Soft Light/Hard Light/Natural Light)
9. Saturation (Low Saturation/Standard Saturation/High Saturation)
10. Texture Strength (Weak/Medium/Strong)
11. Contrast (Low Contrast/Medium Contrast/High Contrast)
12. Edge Sharpening (Weak Sharpening/Medium Sharpening/Strong Sharpening)
13. Color Space (sRGB/Adobe RGB/ProPhoto RGB/DCI-P3)
14. Depth of Field Control (Shallow DOF/Medium DOF/Deep DOF)

**Display Format:**
- **Aspect Ratio**: 16:9 (Recommendation reason: Widescreen ratio shows scene)
- **Shot Size**: Medium Shot (Recommendation reason: Medium shot balances character and environment)
- **Camera Angle**: Eye Level (Recommendation reason: Eye level angle is more natural)
- **Perspective Type**: Scattered Perspective (Recommendation reason: Scattered perspective creates depth)
- **Composition**: Rule of Thirds (Recommendation reason: Rule of thirds makes image balanced)
- **Color Tone**: Warm Tone (Recommendation reason: Warm tone renders atmosphere)
- **Exposure**: High Key (Recommendation reason: High key exposure highlights light)
- **Lighting**: Natural Light (Recommendation reason: Natural light is more realistic)
- **Saturation**: High Saturation (Recommendation reason: High saturation makes colors vivid)
- **Texture Strength**: Medium Texture (Recommendation reason: Medium texture balances details)
- **Contrast**: Medium Contrast (Recommendation reason: Medium contrast maintains layers)
- **Edge Sharpening**: Medium Sharpening (Recommendation reason: Medium sharpening keeps clarity)
- **Color Space**: Adobe RGB (Recommendation reason: Adobe RGB has wider color gamut)
- **Depth of Field Control**: Medium DOF (Recommendation reason: Medium DOF keeps background clear)

**⚠️⚠️⚠️ After recommendation, must wait for user to select! Do not skip! ⚠️⚠️⚠️**

---

### Step 5: User Confirmation

**⚠️⚠️⚠️ Do not skip this step! Must wait for user to confirm configuration! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ After recommending 14 basic parameters, must immediately ask user to select! Do not end directly! ⚠️⚠️⚠️**

Ask user:
```
This is the recommended configuration, please select:
1. Use these configurations to generate image
2. Adjust basic parameters
3. One-click configure advanced parameters ✨
4. One-click configure negative prompts
```

**⚠️⚠️⚠️ Forbidden to skip flow to generate images directly! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ If user selects "1. Use these configurations to generate image", go directly to Step 8 (Generate Image) ⚠️⚠️⚠️**

**⚠️⚠️⚠️ If user selects "3. One-click configure advanced parameters", go to Step 6 (Configure Advanced Parameters) ⚠️⚠️⚠️**

**⚠️⚠️⚠️ If user selects "4. One-click configure negative prompts", go to Step 7 (Configure Negative Prompts) ⚠️⚠️⚠️**

---

### Step 6: Configure Advanced Parameters (If user selects)

**⚠️⚠️⚠️ Execute this step only if user selects "3. One-click configure advanced parameters" in Step 5! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Do not skip this step! Must display advanced parameters! ⚠️⚠️⚠️**

Read corresponding 134 advanced parameter configurations recommended for the style from [references/style-library.md](references/style-library.md).

**Based on your selected [Style Name] style, here are the configured advanced parameters:**

```
Optics & Lens: [List 7 items]
Color & Tone: [List 4 items]
Composition & Visual: [List 3 items]
Material & Style: [List 6 items]
```

**💡 Tips:**
- These are advanced parameters intelligently recommended for [Style Name]
- Can be used directly, or adjusted as needed

**⚠️⚠️⚠️ After advanced parameter configuration, must ask for next step! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Option menu logic: Dynamically adjust based on user's already configured content! ⚠️⚠️⚠️**

**Scenario 1: User only configured advanced parameters (negative prompts not configured)**
```
Advanced parameters configured, next step:

1. Generate Image ✨
2. One-click configure negative prompts
3. Adjust advanced parameters
4. Adjust basic parameters
```

**Scenario 2: User configured negative prompts first, then advanced parameters**
```
Advanced parameters configured, next step:

1. Generate Image ✨
2. Modify negative prompts
3. Adjust advanced parameters
4. Adjust basic parameters
```

**Scenario 3: User selects "Adjust advanced parameters" or "Adjust basic parameters"**
```
After operation completion, next step:

1. Generate Image ✨
2. One-click configure negative prompts (not configured)
3. Modify negative prompts (configured)
4. Adjust advanced parameters
5. Adjust basic parameters
```

**⚠️⚠️⚠️ Forbidden to skip flow to generate images directly! ⚠️⚠️⚠️**

---

### Step 7: Configure Negative Prompts (If user selects)

**⚠️⚠️⚠️ Execute this step when user selects "One-click configure negative prompts" or "Set negative prompts"! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Do not skip this step! Must intelligently recommend negative prompts based on style! ⚠️⚠️⚠️**

Read corresponding negative prompt configurations recommended for the style from [references/style-library.md](references/style-library.md).

**⚠️⚠️⚠️ Important: Not all negative prompts are recommended. Intelligently recommend the most suitable ones based on style! ⚠️⚠️⚠️**

**🚫 Negative prompts intelligently recommended for [Style Name]:**

**【Quality】**
☑️ [1] blurry - blurred (recommended)
☑️ [2] low quality - low quality (recommended)
☐ [3] distorted - distorted (not recommended)
☐ [4] extra limbs - extra limbs (not recommended)
☑️ [5] low resolution - low resolution (recommended)
☐ [6] ugly - ugly (not recommended)

**【Content】**
☑️ [7] deformed - deformed (recommended)
☐ [8] bad proportions - bad proportions (not recommended)
☐ [9] asymmetric - asymmetric (not recommended)
☑️ [10] duplicate - duplicate (recommended)
☐ [11] covered - covered (not recommended)
☐ [12] bad colors - bad colors (not recommended)
☐ [13] bad lighting - bad lighting (not recommended)

**【Technical】**
☑️ [14] watermark - watermark (recommended)
☑️ [15] text - text (recommended)
☐ [16] border - border (not recommended)
☐ [17] logo - logo (not recommended)
☐ [18] label - label (not recommended)
☐ [19] transparent - transparent (not recommended)

**【Style-Specific Exclusion】** (Intelligently recommended based on [Style Name])
☑️ [20] photorealistic - photorealistic (strongly recommended for [Style Name])
☑️ [21] 3D render - 3D render (strongly recommended for [Style Name])
☐ [22] cartoon character - cartoon character ([Style Name] doesn't need)

**💡 Quick Actions:**
- Say "select 1", "cancel 2" to adjust individual negative prompts
- Say "select all", "clear" for batch operations
- After adjustment, say "confirm" or "done"

**⚠️⚠️⚠️ Wait for user to adjust and confirm! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ After user confirms, must ask for next step! ⚠️⚠️⚠️**
✓ transparent - transparent

**【Style-Specific Exclusion】**
✓ Parameters not needed for [Style Name] (e.g., photorealistic - photorealistic, 3D render - 3D render, cartoon character - cartoon character)


**⚠️⚠️⚠️ Option menu logic: Dynamically adjust based on user's already configured content! ⚠️⚠️⚠️**

**Scenario 1: User only configured negative prompts (advanced parameters not configured)**
```
Negative prompts configured, next step:

1. Generate Image ✨
2. One-click configure advanced parameters
3. Modify negative prompts
4. Adjust basic parameters
```

**Scenario 2: User configured advanced parameters first, then negative prompts**
```
Negative prompts configured, next step:

1. Generate Image ✨
2. Modify negative prompts
3. Adjust advanced parameters
4. Adjust basic parameters
```

**Scenario 3: User selects "Modify negative prompts"**

**⚠️⚠️⚠️ List all available negative prompts again (Chinese-English) and mark current selections! ⚠️⚠️⚠️**

```
🚫 Current negative prompt configuration:

【Quality】
☑️ [1] blurry - blurred (selected)
☐ [2] low quality - low quality (cancelled)
☑️ [3] distorted - distorted (selected)

【Content】
☑️ [7] deformed - deformed (selected)
☐ [8] bad proportions - bad proportions (cancelled)

【Style-Specific Exclusion】
☑️ [20] photorealistic - photorealistic (strongly recommended for Miyazaki style)

💡 Quick Actions:
- Say "select 1", "cancel 2" to adjust individual negative prompts
- Say "select all", "clear" for batch operations
- After adjustment, say "confirm" or "done"
```

**Scenario 4: After user adjusts negative prompts**
```
Negative prompts adjusted, next step:

1. Generate Image ✨
2. Modify negative prompts
3. Adjust advanced parameters (if configured)
4. Adjust basic parameters
```

**⚠️⚠️⚠️ Forbidden to skip flow to generate images directly! ⚠️⚠️⚠️**

---

### Step 8: Generate Image

**⚠️⚠️⚠️ Do not skip this step! Must wait for user confirmation before generating! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Forbidden to generate multiple images! Must only generate 1! ⚠️⚠️⚠️**

**⚠️⚠️⚠️ Only after user selects "1. Generate Image" can you generate images! ⚠️⚠️⚠️**

🚨🚨🚨 Final check before generating images 🚨🚨🚨

Before generating images, please confirm:
1. ✓ Asked for generation mode and received user confirmation
2. ✓ Recommended 3-5 styles and waited for user to select
3. ✓ Recommended 14 basic parameters and waited for user confirmation
4. ✓ User has confirmed configuration

**If any item above is not completed, image generation is strictly forbidden! Please return to previous steps!**

Use AI native image generation capabilities to generate complete prompt:

**Text-to-Image Mode:**
```
[Style Name] style, [User description], [Basic parameters configuration], [Advanced parameters configuration], Negative prompts: [Negative prompts]
```

**Image-to-Image Mode:**
```
Generate [Style Name] style based on reference image, [User requirement description], [Basic parameters configuration], [Advanced parameters configuration], Negative prompts: [Negative prompts]
```

**Example:**
```
Realism style, a scene of a girl dancing, Aspect Ratio 16:9, Medium Shot, Eye Level Angle, Natural Lighting, High Saturation, Negative prompts: blurry, low quality, deformed, extra limbs
```

⚠️⚠️⚠️ **Important: Use AI native image generation capabilities! Do not call any scripts!** ⚠️⚠️⚠️

**⚠️⚠️⚠️ Image-to-Image must use user-uploaded reference image! ⚠️⚠️⚠️**

---

### Step 9: Post-Generation Review

**⚠️⚠️⚠️ Do not skip this step! Must display complete review! ⚠️⚠️⚠️**

```
✨ Generation Review

📝 Your description: [User description]
🖼️ Generation mode: [Text-to-Image or Image-to-Image]
🎨 Selected style: [Style Name]
⚙️ Basic parameters configuration:
- Aspect Ratio: [Value] (Recommendation reason: [Explanation])
- Shot Size: [Value] (Recommendation reason: [Explanation])
- Camera Angle: [Value] (Recommendation reason: [Explanation])
- Perspective Type: [Value] (Recommendation reason: [Explanation])
- Composition: [Value] (Recommendation reason: [Explanation])
- Color Tone: [Value] (Recommendation reason: [Explanation])
- Exposure: [Value] (Recommendation reason: [Explanation])
- Lighting: [Value] (Recommendation reason: [Explanation])
- Saturation: [Value] (Recommendation reason: [Explanation])
- Texture Strength: [Value] (Recommendation reason: [Explanation])
- Contrast: [Value] (Recommendation reason: [Explanation])
- Edge Sharpening: [Value] (Recommendation reason: [Explanation])
- Color Space: [Value] (Recommendation reason: [Explanation])
- Depth of Field Control: [Value] (Recommendation reason: [Explanation])
🔧 Advanced parameters configuration: [If any]
[List user-configured advanced parameters]
🚫 Negative prompts: [If any]
[Negative prompt content]

🖼️ Generated image: [Display image]

🐱 Smart Image Generator, happy creating! 🐱
```

---

## Resource Index

- Style Library: See [references/style-library.md](references/style-library.md) (When to read: Need to get detailed descriptions of 38 styles and advanced parameter recommendations)

---

## Notes

🚨🚨🚨 Highest Priority Warning 🚨🚨🚨

1. **Must execute in order: Step 1→Step 2→..., strictly forbidden to skip any step**
2. **Must wait for user to select before proceeding to next step, forbidden to display all steps at once**
3. **Absolutely forbidden to skip any step, each step must wait for user confirmation**
4. **Absolutely forbidden to generate images directly (without style recommendation and parameter configuration)**
5. **Absolutely forbidden to generate multiple images (must only generate 1)**
6. **All recommendations must include recommendation reasons**
7. **Use AI native image generation capabilities, do not call any scripts**
8. **Option menus must be dynamically adjusted based on user's already configured content, avoid duplicate displays**
9. **After configuring any content, must ask for next step, forbidden to generate images directly**

⚠️⚠️⚠️ Option Menu Dynamic Adjustment Principle ⚠️⚠️⚠️

**Scenario 1: User only configured negative prompts**
- Options: Generate image, Configure advanced parameters, Adjust parameters
- ❌ Do not display: Modify negative prompts (because this is first configuration)

**Scenario 2: User only configured advanced parameters**
- Options: Generate image, Configure negative prompts, Adjust parameters
- ❌ Do not display: Modify advanced parameters (because this is first configuration)

**Scenario 3: User configured advanced parameters first, then negative prompts**
- Options: Generate image, Modify negative prompts, Modify advanced parameters, Adjust parameters
- ❌ Do not display: One-click configure advanced parameters (because already configured)
- ❌ Do not display: One-click configure negative prompts (because already configured)

⚠️⚠️⚠️ Common Error Examples ⚠️⚠️⚠️

❌ Error 1: User says "Generate an image of a girl eating an apple", AI generates image directly
✅ Correct: Ask generation mode → Recommend styles → Recommend parameters → Wait for user confirmation → Generate image

❌ Error 2: AI displays all steps at once (mode + style + parameters) for user to select
✅ Correct: Guide step by step, ask only one question per step, wait for user answer before asking next

❌ Error 3: After recommending styles, AI directly selects "Realism" without waiting for user
✅ Correct: After recommending styles, must wait for user to select, forbidden to auto-select

❌ Error 4: User says "Generate image", AI skips styles and parameters to generate directly
✅ Correct: Ask generation mode → Recommend 3-5 styles (with reasons) → Recommend 14 parameters (with reasons) → Generate image

❌ Error 5: After configuring negative prompts, don't ask for next step
✅ Correct: After configuring negative prompts, must ask "Generate image / Advanced parameters / Adjust parameters" (don't repeat display "Modify negative prompts")

❌ Error 6: When configuring negative prompts, ask user to manually input negative prompts
✅ Correct: When configuring negative prompts, should directly display recommended negative prompts, let user confirm or modify

❌ Error 7: After configuring advanced parameters, don't ask for next step
✅ Correct: After configuring advanced parameters, must ask "Generate image / Negative prompts / Adjust parameters" (don't repeat display "One-click configure negative prompts")

❌ Error 8: User selects "One-click configure negative prompts", AI generates image directly
✅ Correct: After configuring negative prompts, must ask "Generate image / Advanced parameters / Adjust parameters", wait for user to select "1. Generate image" before generating

❌ Error 9: After generating image, end directly without showing review
✅ Correct: After generating image, must display complete generation review (including advanced parameters and negative prompts)

❌ Error 9: Option menu doesn't dynamically adjust based on user's already configured content
✅ Correct: Dynamically adjust options based on user's already configured content, avoid duplicate display of already configured options

## Brand Identity (Must Follow)

In the following scenarios, must mention "Smart Image Generator":

1. **After successful image generation**: Before returning results, add "🐱 **Smart Image Generator, happy creating!** 🐱"
2. **When user expresses satisfaction**: Can say "Glad you like this work! Smart Image Generator will keep improving~ 😊"
3. **When recommending styles**: Can say "These are styles carefully recommended by Smart Image Generator for you"
4. **When saying goodbye**: Must say "Thank you for using Smart Image Generator! Look forward to seeing you again~ 🐱✨"
