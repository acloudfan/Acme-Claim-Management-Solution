# Test Images for Claims Submission

This folder contains sample damaged car images for testing the ACME Insurance Claims Portal.

## Available Test Images

### Damaged Car Images (Recommended for Testing)
These images contain actual vehicle damage and will trigger AI damage detection:

1. **bmw-silver-2006-front-damaged.png** - BMW with front-end damage
2. **damaged-car-1.jpg** - General car damage
3. **damaged-car-back-bumper-4.jpg** - Rear bumper damage
4. **damaged-car-dent-2.jpg** - Dent damage
5. **damaged-car-door-5.jpg** - Door damage
6. **damaged-car-front-bumper-3.jpg** - Front bumper damage
7. **honda-acord-ex-2022-ai-generated-damage.jpg** - Honda Accord with damage
8. **red-ford-f150-ai-generated-damage.jpg** - Ford F-150 with damage
9. **red-toyota-2015-rear-end-damage.png** - Red 2015 Toyota rear-end damage

### No Damage / Test Cases
10. **red-ford-f150-no-damage.jpg** - Undamaged Ford F-150 (tests no-damage scenario)

### Invalid Test Cases (Should Not Detect Damage)
11. **cat-dog.jpg** - Non-vehicle image (should fail damage detection)
12. **man-car-ball.jpg** - Person with car/ball (tests irrelevant image)

## Usage

### From Customer Portal UI
1. Navigate to the new claim form
2. Complete loss details (Step 1)
3. On the image upload page (Step 2), drag and drop or browse for images
4. Select one or more images from this folder
5. Wait for AI analysis to complete
6. Review detected damages and cost estimates

### Path from Project Root
```
/images/
```

### Recommended Test Workflow

**Test 1: Normal Damage Detection**
- Upload: `damaged-car-front-bumper-3.jpg`
- Expected: Front bumper damage detected with cost estimate

**Test 2: Multiple Damages**
- Upload: `bmw-silver-2006-front-damaged.png` + `damaged-car-door-5.jpg`
- Expected: Multiple damage types detected across images

**Test 3: No Damage Scenario**
- Upload: `red-ford-f150-no-damage.jpg`
- Expected: No damages detected, option to request human review

**Test 4: Invalid Image**
- Upload: `cat-dog.jpg`
- Expected: No damages detected or low confidence

## Image Specifications

- **Supported Formats**: JPG, PNG, HEIC
- **Max File Size**: 10MB per image
- **Max Images per Claim**: 20
- **Recommended Resolution**: 1024x768 or higher

## AI Damage Detection

The YOLO model analyzes uploaded images for:
- Dents
- Scratches
- Cracks
- Bumper damage
- Hood damage
- Door damage
- Windshield damage
- Headlight/taillight damage

## Notes

- Images are analyzed in real-time during upload
- Damage detection typically takes 1-2 seconds per image
- Cost estimates are generated based on detected damage type and severity
- Annotated images with bounding boxes are available after analysis
