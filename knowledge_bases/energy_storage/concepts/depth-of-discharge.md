---
title: "Depth of Discharge"
type: concept
status: active
tags: ["performance", "battery-health", "fundamental"]
---

# Depth of Discharge

Depth of discharge (DoD) is the percentage of a battery's rated capacity that has been discharged relative to its full charge. A battery discharged to 80% DoD has used 80% of its rated capacity and retains 20%.
([Wikipedia](https://en.wikipedia.org/wiki/Depth_of_discharge))

## Definition and related terms

- **DoD**: fraction of rated capacity discharged (e.g., 80% DoD = 80% used)
- **State of Charge (SoC)**: the complement - SoC + DoD = 100% for a given discharge
- **Rated capacity**: the manufacturer-specified usable energy at defined conditions (temperature, C-rate)

## Why DoD matters

Deeper discharge cycles cause more stress on battery electrodes and electrolyte. For lithium-ion cells:

- Cycling to 100% DoD repeatedly accelerates capacity fade
- Most lithium-ion BESS are designed for [80-90% usable DoD](https://en.wikipedia.org/wiki/Depth_of_discharge) in daily operation, with the top and bottom 5-10% of SoC range reserved as buffer
- [LFP chemistry is more tolerant of full DoD cycles](https://en.wikipedia.org/wiki/Lithium_iron_phosphate_battery) than NMC/NCA, contributing to its longer cycle life

For flow batteries (vanadium), DoD constraints are less binding because energy is stored in liquid electrolyte rather than solid electrodes.

## Impact on system sizing

Operators and manufacturers specify **usable energy** (energy deliverable within the DoD limits) separately from **nameplate energy** (full rated capacity). A 100 MWh nameplate system designed for 90% DoD has 90 MWh of usable energy.

Grid services contracts typically specify requirements in usable MWh, so the difference between nameplate and usable energy is commercially significant.

## DoD and cycle life

The relationship between DoD and cycle life is well established for lithium-ion. Shallower cycles extend battery life significantly:

- 100% DoD: ~500-1,000 cycles to 80% capacity retention (NMC)
- 50% DoD: 2,000-4,000+ cycles
- 20% DoD: 10,000+ cycles

([Battery University: How Depth of Discharge Affects Cycle Life](https://batteryuniversity.com/article/bu-501a-discharge-strategies-for-the-lead-acid-battery))

LFP cells are considerably more resilient, often rated for 2,000-6,000 cycles even at full DoD.

## Sources

- [Wikipedia: Depth of discharge](https://en.wikipedia.org/wiki/Depth_of_discharge)
- [Wikipedia: Lithium iron phosphate battery](https://en.wikipedia.org/wiki/Lithium_iron_phosphate_battery)
- [Battery University: Discharge Strategies](https://batteryuniversity.com/article/bu-501a-discharge-strategies-for-the-lead-acid-battery)

## Related

[[cycle-life]], [[round-trip-efficiency]], [[lithium-ion-battery]]
