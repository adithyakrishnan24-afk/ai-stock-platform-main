let currentValue = 0;

function renderMeter(value) {
  const canvas = document.getElementById("meter");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  const width = canvas.width;
  const height = canvas.height;

  const centerX = width / 2;
  const centerY = height - 20;  // slightly higher for semi-circle
  const radius = 70;

  const target = Math.min(100, Math.max(0, Math.round(value)));

  const color =
    target >= 65 ? "#22c55e" :   // BUY
    target >= 40 ? "#facc15" :   // HOLD
                  "#ef4444";     // SELL

  currentValue = 0;

  function animate() {
    ctx.clearRect(0, 0, width, height);

    /* Background arc */
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
    ctx.lineWidth = 14;
    ctx.strokeStyle = "#1e293b";
    ctx.shadowBlur = 0;
    ctx.stroke();

    /* Progress arc */
    const angle = Math.PI + (currentValue / 100) * Math.PI;

    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, angle);
    ctx.lineWidth = 14;
    ctx.strokeStyle = color;
    ctx.shadowBlur = 15;
    ctx.shadowColor = color;
    ctx.stroke();

    /* Percentage text */
    ctx.shadowBlur = 0;
    ctx.fillStyle = color;
    ctx.font = "bold 20px Segoe UI";
    ctx.textAlign = "center";
    ctx.fillText(`${currentValue}%`, centerX, centerY + 5);

    if (currentValue < target) {
      currentValue++;
      requestAnimationFrame(animate);
    }
  }

  animate();
}