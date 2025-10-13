// --- Configuration ---
epsilon = 0.01; // Small value to prevent Z-fighting

nLayers = 5; // Number of conductive layers above the base layer
layerHeight = 10; // Height of one dielectric layer
plateThickness = 1; // Thickness of the conductive plates
casingInset = 0.5;
casingThickness = 0.5;

// Radii
mainRadius = 50;
baseLayerRadius = 60;
baseTerminalRadius = 75;
dielectricCoreRadius = 12;

// Casing details (previously "mullions")
nSegments = 72;
segmentWidth = 0.4;
segmentDepth = 0.8;


// --- Modules ---

/**
 * Creates a single, complete layer of the capacitor.
 * @param zBottom The Z coordinate for the bottom of the conductive plate.
 * @param radius The outer radius of this layer.
 * @param lHeight The height of the dielectric material for this layer.
 */
module capacitorLayer(zBottom, radius, lHeight) {
  // 1. Conductive Plate
  translate([0, 0, zBottom]) {
    color("saddlebrown") // Copper/Conductive material
      cylinder(h = plateThickness, r = radius, $fn = 128);
  }
  
  // 2. Outer Casing/Insulator for this layer
  // Use epsilon to prevent Z-fighting with plates above and below
  casingHeight = lHeight - plateThickness - (2 * epsilon);
  casingZ = zBottom + plateThickness + epsilon;
  
  translate([0, 0, casingZ]) {
    color([0.67, 0.84, 0.90], 0.4) // Semi-transparent insulator
      difference() {
        outerRadius = radius - casingInset;
        innerRadius = outerRadius - casingThickness;
        
        cylinder(h = casingHeight, r = outerRadius, $fn = 128);
        cylinder(h = casingHeight, r = innerRadius, $fn = 128);
      }
  }
  
  // 3. Casing Segments
  segmentHeight = lHeight - plateThickness;
  segmentZ = zBottom + plateThickness;
  segmentRadius = radius - casingInset - (casingThickness / 2);
  
  translate([0, 0, segmentZ]) {
    for (i = [0 : nSegments - 1]) {
      angle = i * 360 / nSegments;
      
      translate([segmentRadius * cos(angle), segmentRadius * sin(angle), 0]) {
        rotate([0, 0, angle]) {
          color("dimgray")
            cube([segmentDepth, segmentWidth, segmentHeight], center = true);
        }
      }
    }
  }
}

// --- Main Assembly ---

// Base Terminal Plate
translate([0, 0, -plateThickness]) {
  color("darkgray")
    cylinder(h = plateThickness, r = baseTerminalRadius, $fn = 128);
}

// Base Layer (wider and taller dielectric)
baseLayerHeight = layerHeight * 1.5;
capacitorLayer(0, baseLayerRadius, baseLayerHeight);

// Standard Upper Layers
for (i = [0 : nLayers - 1]) {
  zPos = baseLayerHeight + (i * layerHeight);
  capacitorLayer(zPos, mainRadius, layerHeight);
}

// Top Plate/Casing
topPlateZ = baseLayerHeight + (nLayers * layerHeight);
translate([0, 0, topPlateZ]) {
  color("saddlebrown")
    cylinder(h = plateThickness * 1.5, r = mainRadius, $fn = 128);
}

// Central Dielectric Core
coreStartZ = -plateThickness;
coreHeight = plateThickness + baseLayerHeight + (nLayers * layerHeight) + (plateThickness * 1.5);
translate([0, 0, coreStartZ]) {
  color("slategray")
    cylinder(h = coreHeight, r = dielectricCoreRadius, $fn = 128);
}
