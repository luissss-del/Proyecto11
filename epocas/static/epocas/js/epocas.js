// ── Paneles admin: abrir / cerrar ─────────────────────
document.querySelectorAll('.btn-edit-toggle').forEach(btn => {
  btn.addEventListener('click', () => {
    const panelId = btn.dataset.panel;
    const panel   = document.getElementById(panelId);
    if (!panel) return;
    const isOpen = panel.classList.contains('open');
    document.querySelectorAll('.admin-panel').forEach(p => p.classList.remove('open'));
    if (!isOpen) panel.classList.add('open');
  });
});

document.querySelectorAll('.btn-panel-close, .btn-cancel').forEach(btn => {
  btn.addEventListener('click', () => {
    const panelId = btn.dataset.panel;
    const panel   = document.getElementById(panelId);
    if (panel) panel.classList.remove('open');
  });
});

// ── Partículas de fondo ───────────────────────────────
const canvas = document.getElementById('particles');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let W, H, parts = [];

  const resize = () => {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  };
  resize();
  window.addEventListener('resize', resize);

  class Particle {
    constructor() { this.reset(true); }
    reset(init) {
      this.x  = Math.random() * W;
      this.y  = init ? Math.random() * H : H + 10;
      this.r  = Math.random() * 1.2 + 0.3;
      this.vy = -(Math.random() * 0.35 + 0.1);
      this.vx = (Math.random() - 0.5) * 0.14;
      this.a  = Math.random() * 0.12 + 0.04;
    }
    update() { this.x += this.vx; this.y += this.vy; if (this.y < -10) this.reset(false); }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      // Verde suave que combina con el fondo beige
      ctx.fillStyle = `rgba(0,126,110,${this.a})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < 60; i++) parts.push(new Particle());
  (function loop() {
    ctx.clearRect(0, 0, W, H);
    parts.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(loop);
  })();
}

// ── Auto-cerrar mensajes después de 3 segundos ────────
document.querySelectorAll('.msg').forEach(msg => {
  setTimeout(() => {
    msg.style.transition = 'opacity .5s, transform .5s';
    msg.style.opacity = '0';
    msg.style.transform = 'translateY(-10px)';
    setTimeout(() => msg.remove(), 500);
  }, 3000);
});