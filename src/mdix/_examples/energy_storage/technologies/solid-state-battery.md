---
title: "Solid-State Battery"
type: technology
status: active
tags: ["electrochemical", "emerging", "ev"]
energy_density_wh_kg: "300-500"
round_trip_efficiency_pct: "90-95"
typical_duration_hours: "1-6"
maturity: pilot
---

# Solid-State Battery

A battery architecture that replaces the liquid electrolyte in conventional lithium-ion cells with a solid ionic conductor. The solid electrolyte eliminates flammable liquid and enables use of a lithium metal anode, boosting energy density.
([Wikipedia](https://en.wikipedia.org/wiki/Solid-state_battery))

## Why it matters

The liquid electrolyte in lithium-ion cells is flammable and limits the anode material (metallic lithium reacts violently with liquid electrolytes). A solid electrolyte in principle allows:

- **Lithium metal anode**: ~10× higher theoretical energy density than graphite
- **No [[thermal-runaway]] via electrolyte combustion**: major safety improvement
- **Wider temperature range**: better low-temperature performance

## Solid electrolyte classes

- **Oxide (LLZO, NASICON-type)**: high stability, brittle, difficult to manufacture thin; Toyota and Panasonic primary focus
- **Sulfide (LGPS, argyrodites)**: [high ionic conductivity near liquid levels](https://www.nature.com/articles/s41560-021-00898-3), air-sensitive manufacturing
- **Polymer (PEO-based)**: flexible, poor room-temperature conductivity; Bolloré has operated polymer-based EV buses in France
- **Halide**: newer class with high conductivity and moderate stability

([Wikipedia: Solid-state battery](https://en.wikipedia.org/wiki/Solid-state_battery))

## Commercial status (2024-2025)

No mass-market solid-state cells yet. [Toyota targets 2027-2028 for EV production](https://global.toyota/en/newsroom/corporate/39663941.html). [QuantumScape](https://www.quantumscape.com) (partnered with VW) has reported single-layer cells meeting automotive specs; multilayer full cells and manufacturing scale-up remain the key challenges.

Solid-state impact will be felt first in EVs and consumer electronics. For stationary storage, existing LFP chemistries are sufficient for most grid applications.

## Key risks

- Manufacturing: forming uniform, thin solid electrolyte layers at scale is still unsolved
- Interface resistance: solid-solid contact degrades with electrode volume changes during cycling
- Cost: unclear path to parity with LFP

## Sources

- [Wikipedia: Solid-state battery](https://en.wikipedia.org/wiki/Solid-state_battery)
- [Nature Energy: Solid-state electrolytes review](https://www.nature.com/articles/s41560-021-00898-3)
- [Toyota newsroom: Next-generation batteries](https://global.toyota/en/newsroom/corporate/39663941.html)

## Related

[[lithium-ion-battery]], [[energy-density]]
