import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
plt.rcParams['legend.framealpha'] = 1.0
import numpy as np
from scipy import signal

# 1. Parameter der Simulation
f = 5.0  # Frequenz in Hz
T = 1.0 / f  # Periodendauer
fs = 2000  # Abtastrate in Hz
duration = 3 * T  # Zeitfenster: 3 Perioden
t = np.linspace(0, duration, int(fs * duration), endpoint=False)

V_0 = 1.0  # Amplitude des Messsignals in V
init_phase_rad = 0.0  # Start-Phasenverschiebung in rad
init_noise = 0.0  # Start-Rauschlevel
phase_step = np.pi / 4  # Diskrete Schrittweite: 2*pi / 8 = pi / 4


# Hilfsfunktion für schöne Pi-Brüche rechts neben dem Slider
def format_pi_fraction(val):
  k = int(round(val / phase_step))  # Vielfaches von pi/4 (0 bis 8)
  if k == 0:
    return '0'
  gcd = math.gcd(k, 4)
  num = k // gcd
  den = 4 // gcd
  num_str = '' if num == 1 else str(num)
  if den == 1:
    return f'{num_str}π'
  return f'{num_str}π/{den}'


# 2. Signalberechnungs-Funktion (Dual-Phase: X und Y, Phase direkt in rad)
def calculate_signals(phase_rad, noise_level):
  rng = np.random.default_rng(42)
  noise = rng.normal(0, noise_level, size=t.shape)

  # Messsignal: V_sig = V_0 * sin(2*pi*f*t + phi) + Rauschen
  v_sig = V_0 * np.sin(2 * np.pi * f * t + phase_rad) + noise

  # Zwei orthogonale Rechteck-Referenzen (0 und pi/2)
  v_ref_x = signal.square(2 * np.pi * f * t)
  v_ref_y = signal.square(2 * np.pi * f * t + np.pi / 2)

  # Multiplikation in beiden Kanälen
  v_mult_x = v_sig * v_ref_x
  v_mult_y = v_sig * v_ref_y

  # DC-Anteile (X und Y) sowie Gesamtsignal R
  v_dc_x = np.mean(v_mult_x)
  v_dc_y = np.mean(v_mult_y)
  v_r = np.sqrt(v_dc_x**2 + v_dc_y**2)

  return v_sig, v_ref_x, v_ref_y, v_mult_x, v_mult_y, v_dc_x, v_dc_y, v_r


# 3. Initiale Berechnung
v_sig, v_ref_x, v_ref_y, v_mult_x, v_mult_y, v_dc_x, v_dc_y, v_r = (
    calculate_signals(init_phase_rad, init_noise)
)

# 4. Plot-Layout erstellen
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 9.5))
plt.subplots_adjust(left=0.1, bottom=0.18, right=0.95, top=0.94, hspace=0.68)

# Subplot 1: Messsignal + beide Referenzen
(line_sig,) = ax1.plot(
    t * 1000, v_sig, label='Messsignal $V_{sig}(t)$', color='#1f77b4', lw=2
)
ax1.plot(
    t * 1000,
    v_ref_x,
    label='Referenz X (0)',
    color='black',
    ls='-',
    lw=1.0,
    alpha=0.85,
)
ax1.plot(
    t * 1000,
    v_ref_y,
    label='Referenz Y ($\\pi/2$)',
    color='black',
    ls=':',
    lw=1.0,
    alpha=0.85,
)
ax1.set_title(
    '1. Eingangssignal & Orthogonale Referenzen (X und Y)', fontweight='bold'
)
ax1.set_ylabel('Spannung [V]')
ax1.set_ylim(-1.5, 1.5)
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper right', ncol=3,facecolor='white')

# Subplot 2: Multiplizierte Signale (X in Rot, Y in Grün)
(line_mult_x,) = ax2.plot(
    t * 1000,
    v_mult_x,
    label='Produkt X ($V_{sig} \\cdot Ref_X$)',
    color='red',
    lw=1.5,
)
(line_mult_y,) = ax2.plot(
    t * 1000,
    v_mult_y,
    label='Produkt Y ($V_{sig} \\cdot Ref_Y$)',
    color='green',
    lw=1.5,
)
line_dc_x = ax2.axhline(
    v_dc_x, color='red', lw=2, ls='--', label=f'DC X: {v_dc_x:.3f} V'
)
line_dc_y = ax2.axhline(
    v_dc_y, color='green', lw=2, ls='--', label=f'DC Y: {v_dc_y:.3f} V'
)

ax2.fill_between(t * 1000, 0, v_mult_x, color='red', alpha=0.15)
ax2.fill_between(t * 1000, 0, v_mult_y, color='green', alpha=0.15)

ax2.set_title(
    '2. Multiplikation in Kanal X (In-Phase) & Kanal Y (Quadratur)',
    fontweight='bold',
)
ax2.set_xlabel('Zeit [ms]')
ax2.set_ylabel('Spannung [V]')
ax2.set_ylim(-1.5, 1.5)
ax2.grid(True, alpha=0.3)
ax2.legend(loc='upper right', ncol=2)

# Subplot 3: Dual-Phase Ergebnis über 0 bis 2*pi
phases_sweep = np.linspace(0, 2 * np.pi, 400)
dc_max = (2 / np.pi) * V_0

ax3.plot(
    phases_sweep,
    dc_max * np.cos(phases_sweep),
    color='red',
    ls='--',
    alpha=0.7,
    label='Theorie X ($\\propto \\cos\\varphi$)',
)
ax3.plot(
    phases_sweep,
    dc_max * np.sin(phases_sweep),
    color='green',
    ls='--',
    alpha=0.7,
    label='Theorie Y ($\\propto \\sin\\varphi$)',
)
ax3.axhline(
    dc_max,
    color='#1f77b4',
    ls='--',
    lw=1.5,
    alpha=0.7,
    label='Theorie R ($\\sqrt{X^2+Y^2}$)',
)

(point_x,) = ax3.plot([init_phase_rad], [v_dc_x], 'o', color='red', markersize=8)
(point_y,) = ax3.plot(
    [init_phase_rad], [v_dc_y], 'o', color='green', markersize=8
)
(point_r,) = ax3.plot(
    [init_phase_rad],
    [v_r],
    'D',
    color='#1f77b4',
    markersize=8,
    label=f'Betrag R = {v_r:.3f} V',
)

ax3.axhline(0, color='black', lw=0.8)
ax3.set_title(
    '3. Dual-Phase Ergebnis: X und Y schwanken, Betrag R bleibt konstant',
    fontweight='bold',
)
ax3.set_xlabel('Phasenverschiebung $\\varphi$ [rad]')
ax3.set_ylabel('DC-Anteil [V]')
ax3.set_xlim(0, 2 * np.pi)
ax3.set_xticks([i * phase_step for i in range(9)])
ax3.set_xticklabels([
    '0',
    '$\\pi/4$',
    '$\\pi/2$',
    '$3\\pi/4$',
    '$\\pi$',
    '$5\\pi/4$',
    '$3\\pi/2$',
    '$7\\pi/4$',
    '$2\\pi$',
])
ax3.set_ylim(-0.85, 0.85)
ax3.grid(True, alpha=0.3)
ax3.legend(loc='upper right', ncol=2)

# 5. Interaktive Schieberegler (diskrete Schritte von pi/4)
ax_phase = plt.axes([0.15, 0.08, 0.7, 0.025])
ax_noise = plt.axes([0.15, 0.035, 0.7, 0.025])

slider_phase = Slider(
    ax=ax_phase,
    label='Phase $\\varphi$ [rad]',
    valmin=0.0,
    valmax=2 * np.pi,
    valinit=init_phase_rad,
    valstep=phase_step,
)
slider_phase.valtext.set_text(format_pi_fraction(init_phase_rad))

slider_noise = Slider(
    ax=ax_noise,
    label='Rauschen $\\sigma$ [V]',
    valmin=0.0,
    valmax=2.0,
    valinit=init_noise,
    valstep=0.05,
)


# 6. Update-Funktion
def update(val):
  phase_rad = slider_phase.val
  noise = slider_noise.val

  # Bruch-Anzeige rechts neben dem Phasen-Slider aktualisieren
  slider_phase.valtext.set_text(format_pi_fraction(phase_rad))

  v_sig, _, _, v_mult_x, v_mult_y, v_dc_x, v_dc_y, v_r = calculate_signals(
      phase_rad, noise
  )

  # Kurven aktualisieren
  line_sig.set_ydata(v_sig)
  line_mult_x.set_ydata(v_mult_x)
  line_mult_y.set_ydata(v_mult_y)
  line_dc_x.set_ydata([v_dc_x, v_dc_x])
  line_dc_y.set_ydata([v_dc_y, v_dc_y])

  # Beide Füllflächen (rot und grün) sauber entfernen und neu zeichnen
  for coll in list(ax2.collections):
    coll.remove()
  ax2.fill_between(t * 1000, 0, v_mult_x, color='red', alpha=0.15)
  ax2.fill_between(t * 1000, 0, v_mult_y, color='green', alpha=0.15)

  # Legende in Plot 2 aktualisieren
  line_dc_x.set_label(f'DC X: {v_dc_x:.3f} V')
  line_dc_y.set_label(f'DC Y: {v_dc_y:.3f} V')
  ax2.legend(loc='upper right', ncol=2)

  # Punkte & Legende in Plot 3 aktualisieren
  point_x.set_data([phase_rad], [v_dc_x])
  point_y.set_data([phase_rad], [v_dc_y])
  point_r.set_data([phase_rad], [v_r])
  point_r.set_label(f'Betrag R = {v_r:.3f} V')
  ax3.legend(loc='upper right', ncol=2)

  fig.canvas.draw_idle()


slider_phase.on_changed(update)
slider_noise.on_changed(update)

plt.show()