import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import Lenis from 'lenis'

gsap.registerPlugin(ScrollTrigger)

// ─────────────────────────────────────────────────────────────────────────────
// MOBILE MENU
// ─────────────────────────────────────────────────────────────────────────────
function initMobileMenu() {
  const toggle = document.getElementById('mobile-toggle')
  const links = document.querySelector('.nav-links') as HTMLElement | null
  if (!toggle || !links) return

  toggle.addEventListener('click', () => {
    links.classList.toggle('active')
    toggle.classList.toggle('active')
  })

  links.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      links.classList.remove('active')
      toggle.classList.remove('active')
    })
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// COPY BUTTONS
// ─────────────────────────────────────────────────────────────────────────────
function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const code = btn.getAttribute('data-code') || ''
      try {
        await navigator.clipboard.writeText(code)
        const original = btn.textContent
        btn.textContent = 'Copied!'
        gsap.fromTo(btn, { scale: 1.15 }, { scale: 1, duration: 0.3, ease: 'elastic.out(1,0.5)' })
        setTimeout(() => { btn.textContent = original }, 1500)
      } catch {
        // Fallback
      }
    })
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// TERMINAL TYPEWRITER EFFECT
// ─────────────────────────────────────────────────────────────────────────────
function initTerminalAnimation() {
  const lines = document.querySelectorAll('.terminal-line.output')
  lines.forEach(line => {
    const el = line as HTMLElement
    el.style.opacity = '0'
    el.style.transform = 'translateX(-12px)'
  })

  const terminal = document.querySelector('.terminal-preview')
  if (!terminal) return

  ScrollTrigger.create({
    trigger: terminal,
    start: 'clamp(top 85%)',
    once: true,
    onEnter: () => {
      lines.forEach((line, i) => {
        const tl = gsap.timeline({ delay: 0.4 + i * 0.45 })
        tl.to(line, {
          opacity: 1,
          x: 0,
          duration: 0.35,
          ease: 'power3.out',
        })
        // Flash the status icon
        const icon = line.querySelector('.status-icon')
        if (icon) {
          tl.fromTo(icon, { scale: 0, rotation: -90 }, { scale: 1, rotation: 0, duration: 0.3, ease: 'back.out(2)' }, '-=0.2')
        }
        // Highlight text pop
        const highlight = line.querySelector('.highlight-text')
        if (highlight) {
          tl.fromTo(highlight,
            { opacity: 0, y: 4 },
            { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }, '-=0.15')
        }
      })
    },
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// MAGNETIC HOVER EFFECT ON FEATURE CARDS
// ─────────────────────────────────────────────────────────────────────────────
function initCardTilt() {
  document.querySelectorAll('.feature-card').forEach(card => {
    const el = card as HTMLElement
    el.addEventListener('mousemove', (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const cx = rect.width / 2
      const cy = rect.height / 2
      const rotateX = ((y - cy) / cy) * -4
      const rotateY = ((x - cx) / cx) * 4
      gsap.to(el, {
        rotateX,
        rotateY,
        duration: 0.4,
        ease: 'power2.out',
        transformPerspective: 800,
      })
    })
    el.addEventListener('mouseleave', () => {
      gsap.to(el, {
        rotateX: 0,
        rotateY: 0,
        duration: 0.6,
        ease: 'elastic.out(1,0.5)',
      })
    })
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX GLOWS
// ─────────────────────────────────────────────────────────────────────────────
function initParallaxGlows() {
  window.addEventListener('mousemove', (e: MouseEvent) => {
    const x = (e.clientX / window.innerWidth - 0.5) * 2
    const y = (e.clientY / window.innerHeight - 0.5) * 2

    gsap.to('.glow-1', { x: x * 30, y: y * 20, duration: 1.2, ease: 'power2.out' })
    gsap.to('.glow-2', { x: x * -20, y: y * -15, duration: 1.4, ease: 'power2.out' })
    gsap.to('.glow-3', { x: x * 15, y: y * 10, duration: 1.6, ease: 'power2.out' })
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// GSAP ENTRANCE ANIMATIONS
// ─────────────────────────────────────────────────────────────────────────────
function initAnimations() {

  // ── Vertical Reveal over Hero ──
  gsap.to('.hero-reveal-layer', {
    clipPath: 'inset(0% 0% 0% 0%)',
    ease: 'none',
    scrollTrigger: {
      trigger: '.hero-section',
      start: 'top 24px', // Pins exactly where the hero card starts (due to its 24px margin)
      end: '+=100%',
      scrub: true,
      pin: true,
    }
  });

  // ── Hero entrance timeline ──
  const heroTl = gsap.timeline({ defaults: { ease: 'power4.out' } })

  heroTl
    .fromTo('.navbar',
      { y: -80, opacity: 0 },
      { y: 0, opacity: 1, duration: 0.7 }, 0)
    .fromTo('.hero-badge',
      { opacity: 0, y: 24, scale: 0.9 },
      { opacity: 1, y: 0, scale: 1, duration: 0.6 }, 0.15)
    .fromTo('.title-line:first-child',
      { opacity: 0, y: 50, clipPath: 'inset(100% 0 0 0)' },
      { opacity: 1, y: 0, clipPath: 'inset(0% 0 0 0)', duration: 0.9 }, 0.25)
    .fromTo('.title-line.accent',
      { opacity: 0, y: 50, clipPath: 'inset(100% 0 0 0)' },
      { opacity: 1, y: 0, clipPath: 'inset(0% 0 0 0)', duration: 0.9 }, 0.4)
    .fromTo('.hero-subtitle',
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.7 }, 0.65)
    .fromTo('.hero-actions .btn',
      { opacity: 0, y: 20, scale: 0.95 },
      { opacity: 1, y: 0, scale: 1, duration: 0.5, stagger: 0.12 }, 0.85)
    .fromTo('.terminal-preview',
      { opacity: 0, y: 40, scale: 0.96 },
      { opacity: 1, y: 0, scale: 1, duration: 0.9, ease: 'power3.out' }, 1.0)

  // ── Ambient glow float (continuous) ──
  gsap.to('.glow-1', { x: 120, y: 70, duration: 12, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.glow-2', { x: -90, y: -60, duration: 15, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.glow-3', { scale: 1.4, x: 50, y: -30, duration: 10, repeat: -1, yoyo: true, ease: 'sine.inOut' })

  // ── Pipeline section ──
  const pipelineTl = gsap.timeline({
    scrollTrigger: { trigger: '.pipeline-section', start: 'clamp(top 75%)', once: true }
  })
  pipelineTl
    .fromTo('.pipeline-section .section-tag',
      { opacity: 0, y: 20, scale: 0.9 },
      { opacity: 1, y: 0, scale: 1, duration: 0.5 })
    .fromTo('.pipeline-section .section-title',
      { opacity: 0, y: 35 },
      { opacity: 1, y: 0, duration: 0.6 }, '-=0.3')
    .fromTo('.pipeline-section .section-subtitle',
      { opacity: 0, y: 25 },
      { opacity: 1, y: 0, duration: 0.5 }, '-=0.3')
    .fromTo('.pipeline-image-container',
      { opacity: 0, y: 40, scale: 0.98 },
      { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'power3.out' }, '-=0.2')

  // ── Features section ──
  const featuresTl = gsap.timeline({
    scrollTrigger: { trigger: '.features-section', start: 'clamp(top 75%)', once: true }
  })
  featuresTl
    .fromTo('.features-section .section-tag',
      { opacity: 0, y: 20, scale: 0.9 },
      { opacity: 1, y: 0, scale: 1, duration: 0.5 })
    .fromTo('.features-section .section-title',
      { opacity: 0, y: 35 },
      { opacity: 1, y: 0, duration: 0.6 }, '-=0.3')
    .fromTo('.features-section .section-subtitle',
      { opacity: 0, y: 25 },
      { opacity: 1, y: 0, duration: 0.5 }, '-=0.3')

  // Feature cards — stagger with scale + rotation hint
  gsap.fromTo('.feature-card',
    { opacity: 0, y: 50, scale: 0.92, rotateX: 6 },
    {
      opacity: 1, y: 0, scale: 1, rotateX: 0,
      duration: 0.7, stagger: 0.1,
      ease: 'power3.out',
      scrollTrigger: { trigger: '.features-grid', start: 'clamp(top 70%)', once: true }
    }
  )



  // ── About section ──
  const aboutTl = gsap.timeline({
    scrollTrigger: { trigger: '.hero-reveal-layer', start: 'clamp(top 75%)', once: true }
  })
  aboutTl
    .fromTo('.about-heading',
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out' })
    .fromTo('.about-desc p',
      { opacity: 0, x: 20 },
      { opacity: 1, x: 0, duration: 0.6, stagger: 0.1, ease: 'power3.out' }, '-=0.5')
    .fromTo('.about-link',
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.5, ease: 'power3.out' }, '-=0.3')

  // About stat cards — stagger pop-in
  gsap.fromTo('.stat-card',
    { opacity: 0, y: 60, scale: 0.9 },
    {
      opacity: 1, y: 0, scale: 1,
      duration: 0.8, stagger: 0.15,
      ease: 'back.out(1.2)',
      scrollTrigger: { trigger: '.about-stats', start: 'clamp(top 70%)', once: true }
    }
  )

  // ── Footer ──
  gsap.fromTo('.footer-content',
    { opacity: 0, y: 30 },
    {
      opacity: 1, y: 0,
      duration: 0.7, ease: 'power3.out',
      scrollTrigger: { trigger: '.footer-section', start: 'clamp(top 85%)', once: true }
    }
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// SMOOTH SCROLL PROGRESS BAR (top of page)
// ─────────────────────────────────────────────────────────────────────────────
function initScrollProgress() {
  const bar = document.createElement('div')
  bar.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    height: 2px;
    width: 0%;
    background: linear-gradient(90deg, #BC3908, #941b0c, #c44009);
    z-index: 9999;
    transition: none;
    pointer-events: none;
  `
  document.body.appendChild(bar)

  gsap.to(bar, {
    width: '100%',
    ease: 'none',
    scrollTrigger: {
      trigger: document.body,
      start: 'top top',
      end: 'bottom bottom',
      scrub: 0.3,
    }
  })
}

// ─────────────────────────────────────────────────────────────────────────────
// SMOOTH SCROLL (LENIS)
// ─────────────────────────────────────────────────────────────────────────────
function initSmoothScroll() {
  const lenis = new Lenis({
    autoRaf: true,
  });

  // Listen for the scroll event and sync it with ScrollTrigger
  lenis.on('scroll', ScrollTrigger.update);

  // Sync GSAP ticker with Lenis
  gsap.ticker.add((time)=>{
    lenis.raf(time * 1000);
  });
  
  gsap.ticker.lagSmoothing(0);
}

// ─────────────────────────────────────────────────────────────────────────────
// BOOT
// ─────────────────────────────────────────────────────────────────────────────
function boot() {
  initSmoothScroll()
  initMobileMenu()
  initCopyButtons()
  initAnimations()
  initTerminalAnimation()
  initCardTilt()
  initParallaxGlows()
  initScrollProgress()
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot)
} else {
  boot()
}
