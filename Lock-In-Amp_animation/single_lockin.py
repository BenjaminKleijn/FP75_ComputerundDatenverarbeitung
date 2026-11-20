import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
from scipy import signal


# 1. Parameter der Simulation
f = 5.0  # Frequenz in Hz
T = 1.0 / f  # Periodendauer
fs = 2000  # Abtastrate in Hz
duration = 3 * T  # Zeitfenster: 3 Perioden
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

V_0 = 1.0  # Amplitude des Messsignals in V
init_phase_deg = 0.0  # Start-Phasenverschiebung in Grad
init_noise = 0.0  # Start-Rauschlevel


# 2. Signalberechnungs-Funktion
def calculate_signals(phase_deg, noise_level):
    phase_rad = np.deg2rad(phase_deg)
    # Zufälliges Rauschen (fester Seed für ruhige Darstellung beim Schieben)
    rng = np.random.default_rng(42)
    noise = rng.normal(0, noise_level, size=t.shape)

    # Messsignal: V_sig = V_0 * sin(2*pi*f*t + phi) + Rauschen
    v_sig = V_0 * np.sin(2 * np.pi * f * t + phase_rad) + noise

    # Referenzsignal: Rechteckfunktion (-1 bis +1) mit gleicher Frequenz
    v_ref = signal.square(2 * np.pi * f * t)

    # Multiplikation (Mischer-Ausgang)
    v_mult = v_sig * v_ref

    # Gleichspannungsanteil (Mittelwert über ganzzahlige Perioden = idealer Tiefpass)
    v_dc = np.mean(v_mult)

    return v_sig, v_ref, v_mult, v_dc


# 3. Initiale Berechnung
v_sig, v_ref, v_mult, v_dc = calculate_signals(init_phase_deg, init_noise)

# 4. Plot-Layout erstellen
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 9))
plt.subplots_adjust(left=0.1, bottom=0.20, right=0.95, top=0.94, hspace=0.65)

# Subplot 1: Eingangssignal und Rechteck-Referenz
(line_sig,) = ax1.plot(t * 1000, v_sig, label='Messsignal $V_{sig}(t)$', color='#1f77b4', lw=2)
(line_ref,) = ax1.plot(
    t * 1000, v_ref, label='Referenz (Rechteck)', color='black', ls='--', alpha=0.8
)
ax1.set_title('1. Eingangssignal & Referenzfunktion (Chopper)', fontweight='bold')
ax1.set_ylabel('Spannung [V]')
ax1.set_ylim(-1.5, 1.5)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right')

# Subplot 2: Multipliziertes Signal und DC-Anteil
(line_mult,) = ax2.plot(
    t * 1000, v_mult, label='Produkt $V_{sig} \\cdot V_{ref}$', color='red', lw=1.5
)
line_dc = ax2.axhline(
    v_dc, color='green', lw=2.5, label=f'DC-Anteil (Tiefpass): {v_dc:.3f} V'
)
ax2.fill_between(t * 1000, 0, v_mult, color='red', alpha=0.15)
ax2.set_title('2. Multiplikation (Phasenempfindlicher Gleichrichter)', fontweight='bold')
ax2.set_xlabel('Zeit [ms]')
ax2.set_ylabel('Spannung [V]')
ax2.set_ylim(-1.5, 1.5)
ax2.grid(True, alpha=0.3)
legend_ax2 = ax2.legend(loc='upper right')

# Subplot 3: Theoretische Kurve DC-Wert vs. Phasenverschiebung (0° bis 360°)
phases_sweep = np.linspace(0, 360, 361)
# Analytischer DC-Wert für Rechteck-Referenz: (2 / pi) * V_0 * cos(phi)
dc_curve = (2 / np.pi) * V_0 * np.cos(np.deg2rad(phases_sweep))
ax3.plot(
    phases_sweep,
    dc_curve,
    color='gray',
    ls='--',
    label='Theorie: $\\frac{2}{\\pi} V_0 \\cos(\\varphi)$',
)
(point_dc,) = ax3.plot(
    [init_phase_deg], [v_dc], 'ro', markersize=9, label='Aktueller Messwert'
)
ax3.axhline(0, color='black', lw=0.8)
ax3.set_title('3. Gleichspannungsanteil in Abhängigkeit der Phasenverschiebung', fontweight='bold')
ax3.set_xlabel('Phasenverschiebung $\\varphi$ [Grad]')
ax3.set_ylabel('DC-Anteil [V]')
ax3.set_xlim(0, 360)
ax3.set_xticks(np.arange(0, 361, 45))
ax3.set_ylim(-0.8, 0.8)
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper right')

# 5. Interaktive Schieberegler (Slider) hinzufügen
ax_phase = plt.axes([0.15, 0.1, 0.7, 0.03])
ax_noise = plt.axes([0.15, 0.05, 0.7, 0.03])

slider_phase = Slider(
    ax=ax_phase,
    label='Phase $\\varphi$ [°]',
    valmin=0.0,
    valmax=360.0,
    valinit=init_phase_deg,
    valstep=1.0,
)

slider_noise = Slider(
    ax=ax_noise,
    label='Rauschen $\\sigma$ [V]',
    valmin=0.0,
    valmax=2.0,
    valinit=init_noise,
    valstep=0.05,
)


# 6. Update-Funktion bei Reglerbewegung
def update(val):
  phase = slider_phase.val
  noise = slider_noise.val

  v_sig, v_ref, v_mult, v_dc = calculate_signals(phase, noise)

  # Kurven in Plot 1 und 2 aktualisieren
  line_sig.set_ydata(v_sig)
  line_mult.set_ydata(v_mult)
  line_dc.set_ydata([v_dc, v_dc])

  # Grüne Füllfläche sauber entfernen und neu zeichnen (kompatibel mit Matplotlib 3.8+)
  for coll in list(ax2.collections):
    coll.remove()
  ax2.fill_between(t * 1000, 0, v_mult, color='red', alpha=0.15)

  # Legende von Plot 2 mit neuem DC-Wert aktualisieren
  line_dc.set_label(f'DC-Anteil (Tiefpass): {v_dc:.3f} V')
  ax2.legend(loc='upper right')

  # Roten Punkt in Plot 3 aktualisieren
  point_dc.set_data([phase], [v_dc])

  fig.canvas.draw_idle()


slider_phase.on_changed(update)
slider_noise.on_changed(update)

plt.show()
