import './style.css'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

// ─────────────────────────────────────────────────────────────────────────────
// CONFIG
// ─────────────────────────────────────────────────────────────────────────────
const TOTAL_FRAMES = 51
const FRAME_DIR    = '/ezgif-6291e59b57acc477-jpg'

const CAPTIONS = [
  { from: 0,  title: 'Decentralized Computing',      desc: 'A new kind of intelligence is emerging — one that swarms.' },
  { from: 10, title: 'Evolving Through the Network', desc: 'Agents negotiate, reason, and self-organise across any infrastructure.' },
  { from: 25, title: 'Connected to Everything',      desc: 'Circuit-level orchestration. Zero single points of failure.' },
  { from: 38, title: 'Swarm Intelligence Unleashed', desc: 'Dozens of autonomous peers collaborating as one unified system.' },
  { from: 46, title: 'Access Granted',               desc: 'Decentralized & secured swarm network — running at full capacity.' },
]

function frameUrl(i: number) {
  return `${FRAME_DIR}/ezgif-frame-${String(i).padStart(3, '0')}.jpg`
}

// ─────────────────────────────────────────────────────────────────────────────
// SCROLL FRAME ANIMATION
// ─────────────────────────────────────────────────────────────────────────────
function initScrollFrameAnimation() {
  const section   = document.getElementById('scroll-anim')     as HTMLElement | null
  const canvas    = document.getElementById('frame-canvas')    as HTMLCanvasElement | null
  const label     = document.getElementById('scroll-anim-label') as HTMLElement | null
  const titleEl   = document.getElementById('scroll-anim-title') as HTMLElement | null
  const descEl    = document.getElementById('scroll-anim-desc')  as HTMLElement | null
  const heroOver  = document.querySelector('.hero-overlay')       as HTMLElement | null
  const heroCont  = document.querySelector('.hero-content')       as HTMLElement | null
  const scrollInd = document.querySelector('.scroll-indicator')   as HTMLElement | null

  if (!section || !canvas) {
    console.error('[FrameAnim] Missing elements:', { section, canvas })
    return
  }

  const ctx = canvas.getContext('2d')!

  // ── All state declared up front (before any function uses them) ──────────
  // This avoids the Temporal Dead Zone (TDZ) / "cannot access before init" error
  const imgs: HTMLImageElement[] = []
  let currentFrame = 0
  let lastCapIdx   = -1

  // ── Helpers ─────────────────────────────────────────────────────────────
  function drawFrame(idx: number) {
    const img = imgs[idx]
    if (!img || !img.complete || img.naturalWidth === 0) {
      // Fall back to nearest already-loaded frame
      for (let j = idx - 1; j >= 0; j--) {
        if (imgs[j]?.complete && imgs[j].naturalWidth > 0) {
          drawFrame(j)
          return
        }
      }
      return
    }
    const cw = canvas!.width
    const ch = canvas!.height
    const iw = img.naturalWidth
    const ih = img.naturalHeight
    // Cover mode: fill canvas, crop edges
    const scale = Math.max(cw / iw, ch / ih)
    const dw = iw * scale, dh = ih * scale
    const dx = (cw - dw) / 2, dy = (ch - dh) / 2
    ctx.clearRect(0, 0, cw, ch)
    ctx.drawImage(img, dx, dy, dw, dh)
  }

  function updateCaption(frameIdx: number) {
    let capIdx = 0
    for (let i = CAPTIONS.length - 1; i >= 0; i--) {
      if (frameIdx >= CAPTIONS[i].from) { capIdx = i; break }
    }
    if (capIdx === lastCapIdx) return
    lastCapIdx = capIdx
    if (!label || !titleEl || !descEl) return
    label.classList.remove('visible')
    setTimeout(() => {
      titleEl!.textContent = CAPTIONS[capIdx].title
      descEl!.textContent  = CAPTIONS[capIdx].desc
      label!.classList.add('visible')
    }, 250)
  }

  // ── Resize canvas to fill viewport ──────────────────────────────────────
  function resize() {
    canvas!.width  = window.innerWidth
    canvas!.height = window.innerHeight
    drawFrame(currentFrame)  // safe — currentFrame is already declared above
  }

  window.addEventListener('resize', resize)
  resize()

  // ── Preload images ───────────────────────────────────────────────────────
  function preload() {
    for (let i = 1; i <= TOTAL_FRAMES; i++) {
      const img   = new Image()
      img.src     = frameUrl(i)
      imgs[i - 1] = img

      img.onload = () => {
        // Draw this frame if it matches the current one
        if (i - 1 === currentFrame) drawFrame(currentFrame)
        // Frame 1: show immediately and reveal captions
        if (i === 1) {
          drawFrame(0)
          if (label) label.classList.add('visible')
        }
      }

      img.onerror = () => {
        console.warn('[FrameAnim] 404:', frameUrl(i))
      }
    }
  }

  // ── Scroll handler ───────────────────────────────────────────────────────
  function onScroll() {
    const rect     = section!.getBoundingClientRect()
    const sectionH = section!.offsetHeight
    const viewH    = window.innerHeight

    // progress goes 0→1 as the section scrolls through the viewport
    const scrolled = -rect.top
    const total    = sectionH - viewH
    const progress = Math.max(0, Math.min(1, scrolled / total))

    // Drive frame index
    const targetFrame = Math.min(Math.floor(progress * TOTAL_FRAMES), TOTAL_FRAMES - 1)
    if (targetFrame !== currentFrame) {
      currentFrame = targetFrame
      drawFrame(currentFrame)
      updateCaption(currentFrame)
    }

    // Fade hero overlay out over first 15% of scroll
    const heroP = Math.min(1, progress / 0.15)
    if (heroOver)  heroOver.style.opacity   = String(1 - heroP)
    if (heroCont)  heroCont.style.transform  = `translateY(${-heroP * 60}px)`
    if (scrollInd) scrollInd.style.opacity  = String(1 - heroP)
  }

  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll() // run once on init

  // Set initial caption text
  if (titleEl) titleEl.textContent = CAPTIONS[0].title
  if (descEl)  descEl.textContent  = CAPTIONS[0].desc

  preload()
  console.log('[FrameAnim] Initialized | frames:', TOTAL_FRAMES)
}

// ─────────────────────────────────────────────────────────────────────────────
// GSAP ENTRANCE ANIMATIONS
// ─────────────────────────────────────────────────────────────────────────────
function initAnimations() {

  // Hero entrance
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  tl.fromTo('.hero-badge',        { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, 0.2)
    .fromTo('.title-line',        { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, stagger: 0.2 }, 0.2)
    .fromTo('.hero-subtitle',     { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7 }, 0.6)
    .fromTo('.hero-actions .btn', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.15 }, 0.8)
    .fromTo('.scroll-indicator',  { opacity: 0 },         { opacity: 1, duration: 0.5 }, 1.0)

  // Navbar
  gsap.fromTo('.navbar',
    { y: -80, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.6, ease: 'power3.out', delay: 0.1 }
  )

  // Orbs
  gsap.to('.orb-1', { x: 150, y: 100,  duration: 8,  repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.orb-2', { x: -120, y: -80, duration: 10, repeat: -1, yoyo: true, ease: 'sine.inOut' })
  gsap.to('.orb-3', { scale: 1.3,      duration: 6,  repeat: -1, yoyo: true, ease: 'sine.inOut' })

  // Features section
  gsap.fromTo('.section-title',
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out',
      scrollTrigger: { trigger: '.features-section', start: 'top 80%' } }
  )
  gsap.fromTo('.section-subtitle',
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out',
      scrollTrigger: { trigger: '.features-section', start: 'top 75%' } }
  )
  gsap.fromTo('.feature-card',
    { opacity: 0, y: 50, scale: 0.95 },
    { opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'power3.out', stagger: 0.15,
      scrollTrigger: { trigger: '.features-grid', start: 'top 70%' } }
  )

  // About section
  gsap.fromTo('.about-section .section-title',
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out',
      scrollTrigger: { trigger: '.about-section', start: 'top 80%' } }
  )
  gsap.fromTo('.about-text p',
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.15,
      scrollTrigger: { trigger: '.about-text', start: 'top 75%' } }
  )
  gsap.fromTo('.about-highlight',
    { opacity: 0, scale: 0.9 },
    { opacity: 1, scale: 1, duration: 0.7, ease: 'elastic.out(1,0.5)',
      scrollTrigger: { trigger: '.about-highlight', start: 'top 85%' } }
  )

  // Footer section
  gsap.fromTo('.footer-section .section-title',
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out',
      scrollTrigger: { trigger: '.footer-section', start: 'top 80%' } }
  )
  gsap.fromTo('.footer-subtitle',
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out',
      scrollTrigger: { trigger: '.footer-subtitle', start: 'top 75%' } }
  )
  gsap.fromTo('.footer-actions .btn',
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.15,
      scrollTrigger: { trigger: '.footer-actions', start: 'top 85%' } }
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// BOOT
// ─────────────────────────────────────────────────────────────────────────────
function boot() {
  initAnimations()
  initScrollFrameAnimation()
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot)
} else {
  boot()
}
