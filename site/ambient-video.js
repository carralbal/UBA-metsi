(() => {
  const clips = [...document.querySelectorAll('[data-ambient-video]')];
  if (!clips.length) return;

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
  const conserveData = () => Boolean(connection?.saveData || ['slow-2g', '2g'].includes(connection?.effectiveType));
  const stopAll = () => clips.forEach((clip) => clip.pause());
  const isVisible = (clip) => {
    const box = clip.getBoundingClientRect();
    return box.top < innerHeight * .82 && box.bottom > innerHeight * .18;
  };
  const update = () => {
    if (document.hidden || motion.matches || conserveData()) {
      stopAll();
      return;
    }
    let playing = false;
    for (const clip of clips) {
      if (!playing && isVisible(clip)) {
        const source = clip.querySelector('source');
        if (source?.dataset.src && !source.src) {
          source.src = source.dataset.src;
          clip.load();
        }
        clip.play().catch(() => {});
        playing = true;
      } else clip.pause();
    }
  };
  let queued = false;
  const schedule = () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(() => { queued = false; update(); });
  };
  motion.addEventListener?.('change', schedule);
  connection?.addEventListener?.('change', schedule);
  document.addEventListener('visibilitychange', schedule);
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  update();
})();
