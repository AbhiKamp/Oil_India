# Petroleum Engineering Basis & Mathematical Formulations
## Physics-Constrained Analytics for StrataSentry-NWIS

---

## 1. 3D Wellbore Directional Geometry: Minimum Curvature Method (MCM)

The Minimum Curvature Method is the global petroleum industry standard (SPE / API) for calculating 3D directional borehole trajectories. It models the wellbore path between two consecutive survey stations as a circular arc in a plane of curvature.

Given two survey points $S_1(MD_1, I_1, A_1)$ and $S_2(MD_2, I_2, A_2)$, where:
- $MD$: Measured Depth (meters)
- $I$: Borehole Inclination angle (radians)
- $A$: Borehole Azimuth angle (radians)

### 1.1 Dogleg Angle ($\beta$)
$$\beta = \arccos\big(\cos I_1 \cos I_2 + \sin I_1 \sin I_2 \cos(A_2 - A_1)\big)$$

### 1.2 Ratio Factor ($F$)
$$F = \begin{cases} 
1.0 & \text{if } \beta < 10^{-6} \\
\frac{2}{\beta} \tan\left(\frac{\beta}{2}\right) & \text{otherwise}
\end{cases}$$

### 1.3 Coordinate Increments
$$\Delta TVD = \frac{\Delta MD}{2} (\cos I_1 + \cos I_2) F$$
$$\Delta \text{North} = \frac{\Delta MD}{2} (\sin I_1 \cos A_1 + \sin I_2 \cos A_2) F$$
$$\Delta \text{East} = \frac{\Delta MD}{2} (\sin I_1 \sin A_1 + \sin I_2 \sin A_2) F$$

### 1.4 Dogleg Severity ($DLS$)
$$DLS = \frac{\beta}{\Delta MD} \times 30 \times \left(\frac{180}{\pi}\right) \quad [^\circ / 30\text{ m}]$$

---

## 2. Drilling Hydraulics & Dynamic Equivalent Circulating Density (ECD)

### 2.1 Bingham Plastic Rheological Model
Drilling mud shear stress ($\tau$) relates to shear rate ($\gamma$) via Yield Point ($YP$) and Plastic Viscosity ($PV$):
$$\tau = YP + PV \cdot \gamma$$

The effective annular fluid velocity ($v_{ann}$) for pump flow rate $Q$ (gpm or LPM) in a hole of diameter $D_h$ with drill pipe outer diameter $D_p$:
$$v_{ann} = \frac{24.51 \cdot Q}{D_h^2 - D_p^2} \quad [\text{ft/min}]$$

### 2.2 Annular Pressure Loss ($\Delta P_a$)
$$\Delta P_a = \left(\frac{PV \cdot v_{ann}}{60,000 (D_h - D_p)^2} + \frac{YP}{200 (D_h - D_p)}\right) \cdot TVD$$

### 2.3 Dynamic Equivalent Circulating Density (ECD)
Static mud weight ($\rho_{mud}$) increases dynamically during circulation due to annular friction losses and cuttings loading:
$$ECD = \rho_{mud} + \frac{\Delta P_a}{0.052 \cdot TVD} + \rho_{cuttings\_loading}$$

Where the cuttings volumetric concentration effect ($C_v$) is:
$$\rho_{cuttings\_loading} = \frac{C_v (\rho_{rock} - \rho_{mud})}{1 - C_v}$$

---

## 3. Stuck Pipe Physics & Mechanisms

StrataSentry models three distinct mechanical and differential sticking regimes:

### 3.1 Differential Sticking
Occurs across permeable formations (e.g., Tipam sandstone) when hydrostatic pressure significantly exceeds formation pore pressure ($P_{hydro} - P_{pore} > 0$):
$$F_{pull} = \Delta P \cdot A_c \cdot \mu_f$$
Where:
- $\Delta P = P_{hydro} - P_{pore}$ (Overbalance pressure, psi)
- $A_c = h_{cake} \cdot L_{contact}$ (Mud cake contact area)
- $\mu_f$ = Mud cake friction coefficient ($0.08 - 0.25$)

### 3.2 Mechanical Hole Pack-Off / Bridging
Occurs in swelling or splintery shales (e.g., Barail coal or Kopili shale) when cavings collapse into the annulus:
- Characterized by: $\frac{d(SPP)}{dt} > 0$ (pressure surge) accompanied by sudden loss of rotation and erratic torque spikes.
- Mitigation SOP: Pick up off bottom immediately, establish circulation with low RPM to break bridges, do not jar down initially.

### 3.3 Key Seating
Occurs in doglegs ($DLS > 3^\circ / 30\text{ m}$) where drillpipe wears a narrow slot in the borehole wall.

---

## 4. Well Control & Kick Influx Hydraulics

When formation pore pressure exceeds wellbore hydrostatic head, formation fluid enters the well:
1. **Pit Gain Rate**: $\frac{d V_{pit}}{dt} > 0$ with pumps running at constant rate.
2. **Flow Out vs Flow In Divergence**: $Q_{out} > Q_{in}$.
3. **Shut-In Drillpipe Pressure (SIDPP)**:
   $$P_{pore} = P_{hydrostatic} + SIDPP$$
   $$MW_{kill} = \rho_{mud} + \frac{SIDPP}{0.052 \cdot TVD}$$
