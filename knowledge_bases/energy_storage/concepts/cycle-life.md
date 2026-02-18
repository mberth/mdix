---
title: "Cycle Life"
type: concept
status: active
tags: ["performance", "battery-health", "economics", "fundamental"]
---

# Cycle Life

Cycle life is the number of complete charge-discharge cycles a storage system can perform before its capacity degrades to a defined threshold, typically 80% of initial rated capacity. It directly determines the economic lifetime of a battery system.
([Wikipedia](https://en.wikipedia.org/wiki/Rechargeable_battery#Cycle_life))

## Definition

One cycle = one full charge + one full discharge. Partial cycles are counted proportionally (e.g., two 50% DoD cycles ≈ one full cycle).

The 80% capacity retention threshold (end of life, or EoL) is a common convention but not universal - some contracts or warranty terms use 70% or other thresholds.

## Values by technology

| Technology | Typical cycle life (to 80% capacity) |
|---|---|
| Lithium-ion NMC | 500-2,000 |
| Lithium-ion LFP | 2,000-6,000+ |
| Vanadium flow battery | Effectively unlimited (electrolyte doesn't degrade) |
| Lead-acid | 300-500 |
| Solid-state (projected) | 1,000-5,000+ |

([Wikipedia: Rechargeable battery](https://en.wikipedia.org/wiki/Rechargeable_battery#Cycle_life), [Battery University](https://batteryuniversity.com/article/bu-501-basics-about-discharging))

## Economic implications

Cycle life is a key input into levelized cost of storage (LCOS) calculations:

```
LCOS ≈ (Capital cost) / (Lifetime energy throughput)
     = (Capital cost) / (Usable capacity × Cycle life × DoD)
```

A system with twice the cycle life at the same capital cost delivers energy at roughly half the cost per MWh cycled - all else equal.

This is why LFP has largely displaced NMC in stationary storage: its longer cycle life and lower risk of thermal runaway outweigh the lower energy density, which doesn't matter for ground-mounted BESS.

## Factors affecting cycle life

- **Depth of discharge**: shallower cycles extend life significantly (see [[depth-of-discharge]])
- **Temperature**: high temperatures accelerate degradation in most lithium chemistries; LFP is more tolerant than NMC
- **C-rate**: faster charge/discharge rates stress electrodes; sustained high C-rate operation reduces cycle life
- **Cell chemistry**: LFP has inherently more stable cathode structure under cycling than NMC

## Calendar aging vs. cycle aging

Batteries degrade both with use (cycle aging) and with time (calendar aging), even if not cycled. Calendar aging is driven by temperature and SoC at rest. For a BESS that cycles once daily, calendar aging may be the binding constraint after 10-15 years, even if cycle life hasn't been reached.

## Warranty structures

Utility-scale BESS warranties typically specify a guaranteed minimum capacity (e.g., 80%) at end of a defined period (e.g., 10 years or 3,650 cycles, whichever comes first), plus a throughput guarantee (total MWh deliverable). Vendors like [[catl]] have made high-profile claims about extended degradation guarantees.

## Sources

- [Wikipedia: Rechargeable battery - Cycle life](https://en.wikipedia.org/wiki/Rechargeable_battery#Cycle_life)
- [Battery University: Basics About Discharging](https://batteryuniversity.com/article/bu-501-basics-about-discharging)

## Related

[[depth-of-discharge]], [[round-trip-efficiency]], [[lithium-ion-battery]], [[vanadium-flow-battery]]
