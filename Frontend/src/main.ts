import './style.css'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

function initAnimations() {

  // ── Hero entrance ──
  const heroTl = gsap.timeline({ defaults: { ease: 'power3.out' } })

  heroTl
    .fromTo('.hero-badge', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6 }, 0.2)
    .fromTo('.title-line', { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, stagger: 0.2 }, 0.2)
    .fromTo('.hero-subtitle', { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.7 }, 0.6)
    .fromTo('.hero-actions .btn', { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, stagger: 0.15 }, 0.8)
    .fromTo('.scroll-indicator', { opacity: 0 }, { opacity: 1, duration: 0.5 }, 1.0)

  // ── Navbar slide ──
  gsap.fromTo('.navbar', { y: -80, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, ease: 'power3.out', delay: 0.1 })

  // ── Orbs ──
  gsap.to('.orb-1', {
    x: 150, y: 100, duration: 8,
    repeat: -1, yoyo: true, ease: 'sine.inOut',
  })
  gsap.to('.orb-2', {
    x: -120, y: -80, duration: 10,
    repeat: -1, yoyo: true, ease: 'sine.inOut',
  })
  gsap.to('.orb-3', {
    scale: 1.3, duration: 6,
    repeat: -1, yoyo: true, ease: 'sine.inOut',
  })

  // ── Features section ──
  gsap.fromTo('.section-title',
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out', scrollTrigger: { trigger: '.features-section', start: 'top 80%' } }
  )
  gsap.fromTo('.section-subtitle',
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', scrollTrigger: { trigger: '.features-section', start: 'top 75%' } }
  )
  gsap.fromTo('.feature-card',
    { opacity: 0, y: 50, scale: 0.95 },
    {
      opacity: 1, y: 0, scale: 1, duration: 0.7, ease: 'power3.out',
      stagger: 0.15,
      scrollTrigger: { trigger: '.features-grid', start: 'top 70%' },
    }
  )

  // ── About section ──
  gsap.fromTo('.about-section .section-title',
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out', scrollTrigger: { trigger: '.about-section', start: 'top 80%' } }
  )
  gsap.fromTo('.about-text p',
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.15, scrollTrigger: { trigger: '.about-text', start: 'top 75%' } }
  )
  gsap.fromTo('.about-highlight',
    { opacity: 0, scale: 0.9 },
    { opacity: 1, scale: 1, duration: 0.7, ease: 'elastic.out(1, 0.5)', scrollTrigger: { trigger: '.about-highlight', start: 'top 85%' } }
  )

  // ── Footer section ──
  gsap.fromTo('.footer-section .section-title',
    { opacity: 0, y: 40 },
    { opacity: 1, y: 0, duration: 0.7, ease: 'power3.out', scrollTrigger: { trigger: '.footer-section', start: 'top 80%' } }
  )
  gsap.fromTo('.footer-subtitle',
    { opacity: 0, y: 30 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', scrollTrigger: { trigger: '.footer-subtitle', start: 'top 75%' } }
  )
  gsap.fromTo('.footer-actions .btn',
    { opacity: 0, y: 20 },
    { opacity: 1, y: 0, duration: 0.6, ease: 'power3.out', stagger: 0.15, scrollTrigger: { trigger: '.footer-actions', start: 'top 85%' } }
  )
}

// Wait for page to load, then init
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAnimations)
} else {
  initAnimations()
}
