---
title: "Energy Density"
type: concept
status: active
tags: ["performance", "fundamental", "comparison"]
---

# Energy Density

Energy density measures how much energy a storage system holds per unit of mass (gravimetric, Wh/kg) or per unit of volume (volumetric, Wh/L). It determines the physical footprint and weight of a storage system for a given energy capacity.
([Wikipedia](https://en.wikipedia.org/wiki/Energy_density))

## Gravimetric vs. volumetric

- **Gravimetric energy density (Wh/kg)**: critical for mobile applications (EVs, aircraft) where weight is a constraint
- **Volumetric energy density (Wh/L)**: critical for space-constrained installations

For stationary grid storage, neither is typically the binding constraint - land and capital cost dominate. However, for urban or rooftop installations, volumetric density matters.

## Values by technology

| Technology | Gravimetric (Wh/kg) | Volumetric (Wh/L) |
|---|---|---|
| Lithium-ion NMC | 200-300 | 400-700 |
| Lithium-ion LFP | 120-180 | 250-450 |
| Solid-state (target) | 300-500 | 600-1,000 |
| Vanadium flow battery | 15-25 | 20-35 |
| Pumped hydro | ~0.3 | ~0.3 |
| Iron-air battery | 20-30 | 25-40 |
| Hydrogen (compressed) | 33,000 (fuel only) | 1,000 (at 700 bar) |

(Sources: [Wikipedia: Comparison of commercial battery types](https://en.wikipedia.org/wiki/Comparison_of_commercial_battery_types), [Wikipedia: Energy density](https://en.wikipedia.org/wiki/Energy_density))

## Practical significance for grid storage

For utility-scale BESS, energy density affects:

- **Site footprint**: a 100 MWh LFP system occupies significantly less land than a 100 MWh vanadium flow system
- **Shipping and installation cost**: higher density = fewer containers, less civil work
- **Indoor vs. outdoor deployment**: high-density systems can be building-integrated (as at [[moss-landing-energy-storage]]); lower-density systems typically need outdoor pads

## Energy density vs. specific energy

In practice, "energy density" is often used loosely to refer to gravimetric energy density (Wh/kg), also called **specific energy**. The strict distinction:

- Energy density = energy per unit volume (Wh/L)
- Specific energy = energy per unit mass (Wh/kg)

Both matter for different applications.

## Sources

- [Wikipedia: Energy density](https://en.wikipedia.org/wiki/Energy_density)
- [Wikipedia: Comparison of commercial battery types](https://en.wikipedia.org/wiki/Comparison_of_commercial_battery_types)

## Related

[[lithium-ion-battery]], [[solid-state-battery]], [[vanadium-flow-battery]], [[round-trip-efficiency]]
