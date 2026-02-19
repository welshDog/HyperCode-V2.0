"use client"
import React, { useEffect, useState } from "react"
import styles from './support.module.css'

export default function Page() {
  const [reducedMotion, setReducedMotion] = useState(false)
  const [dyslexicFont, setDyslexicFont] = useState(false)
  const [focusMode, setFocusMode] = useState(false)
  const [stats, setStats] = useState({
    supporters: 0,
    discordCount: 0,
    fundingCurrent: 0,
    fundingGoal: 10000,
    currency: "$"
  })

  useEffect(() => {
    const rm = localStorage.getItem('reduced-motion') === 'true'
    const df = localStorage.getItem('dyslexic-font') === 'true'
    const fm = localStorage.getItem('focus-mode') === 'true'
    setReducedMotion(rm)
    setDyslexicFont(df)
    setFocusMode(fm)

    // Fetch live stats
    fetch('/api/support/stats')
      .then(res => res.json())
      .then(data => {
        setStats(prev => ({ ...prev, ...data }))
      })
      .catch(err => console.error('Failed to load stats', err))
  }, [])

  const toggle = (key: 'reduced-motion' | 'dyslexic-font' | 'focus-mode') => {
    const next = !(key === 'reduced-motion' ? reducedMotion : key === 'dyslexic-font' ? dyslexicFont : focusMode)
    localStorage.setItem(key, String(next))
    if (key === 'reduced-motion') {
      setReducedMotion(next)
    } else if (key === 'dyslexic-font') {
      setDyslexicFont(next)
    } else {
      setFocusMode(next)
    }
  }

  const fundingPercent = stats.fundingGoal > 0 ? Math.min(100, Math.round((stats.fundingCurrent / stats.fundingGoal) * 100)) : 0

  const containerClasses = [
    styles.container,
    reducedMotion && styles.reducedMotion,
    dyslexicFont && styles.dyslexicFont,
    focusMode && styles.focusMode
  ].filter(Boolean).join(' ')

  return (
    <main className={containerClasses} style={{ paddingTop: 24, paddingBottom: 24 }}>
      {/* Crisis Banner */}
      <div style={{ 
        backgroundColor: '#ff4444', 
        color: 'white', 
        padding: '12px', 
        textAlign: 'center', 
        borderRadius: '8px', 
        marginBottom: '20px', 
        fontWeight: 'bold',
        boxShadow: '0 4px 12px rgba(255, 68, 68, 0.3)'
      }}>
        🚨 SAVE HYPERCODE: We need your help to keep the lights on! 🚨
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <h1 style={{ margin: 0 }}>Support Hub (React)</h1>
        <a href="/" style={{ display: 'inline-block', padding: '6px 10px', border: '1px solid #ddd', borderRadius: 6, textDecoration: 'none', color: '#111' }}>Back to Terminal</a>
      </div>

      <div className={styles.accessibilityControls}>
        <button className={styles.accessibilityBtn} aria-label="Toggle reduced motion" aria-pressed={reducedMotion} onClick={() => toggle('reduced-motion')}><span aria-hidden="true">🎬</span> Motion</button>
        <button className={styles.accessibilityBtn} aria-label="Toggle dyslexia-friendly font" aria-pressed={dyslexicFont} onClick={() => toggle('dyslexic-font')}><span aria-hidden="true">🔤</span> Font</button>
        <button className={styles.accessibilityBtn} aria-label="Toggle focus mode" aria-pressed={focusMode} onClick={() => toggle('focus-mode')}><span aria-hidden="true">🎯</span> Focus</button>
      </div>

      <div className={styles.backgroundAnimation}></div>

      <header className={styles.header}>
        <h1>
          <span aria-label="diamond with sparkle" role="img">💎⚡</span>
          SUPPORT THE HYPERFOCUS EMPIRE
          <span aria-label="lightning bolt with diamond" role="img">⚡💎</span>
        </h1>
        <p>Join <strong>ADHD warriors</strong> building the future of neurodivergent-friendly productivity tools! Your support fuels our mission to revolutionize how ADHD minds work, create, and thrive.</p>
        <div className={styles.headerStats}>
          <div className={styles.statItem}><span className={styles.statNumber}>{stats.supporters}</span><span className={styles.statLabel}>Active Supporters</span></div>
          <div className={styles.statItem}><span className={styles.statNumber}>${stats.fundingCurrent}</span><span className={styles.statLabel}>Monthly Goal Progress</span></div>
          <div className={styles.statItem}><span className={styles.statNumber}>{fundingPercent}%</span><span className={styles.statLabel}>Funding Complete</span></div>
        </div>
      </header>

      <section className={styles.quickActions}>
        <h2 className={styles.srOnly}>Quick Support Actions</h2>
        <div className={styles.quickActionGrid}>
          <a href="https://ko-fi.com/hyperfocuszone" className={`${styles.quickBtn} ${styles.quickBtnCoffee}`} target="_blank" rel="noopener noreferrer"><span aria-label="coffee cup" role="img">☕</span><span>Buy Coffee<br/><small>$3 - Quick Thanks</small></span></a>
          <a href="https://patreon.com/hyperfocuszone" className={`${styles.quickBtn} ${styles.quickBtnPopular}`} target="_blank" rel="noopener noreferrer"><span aria-label="star" role="img">⭐</span><span>Most Popular<br/><small>$15/mo - Elite Agent</small></span></a>
          <a href="mailto:business@hyperfocuszone.com" className={`${styles.quickBtn} ${styles.quickBtnBusiness}`}><span aria-label="briefcase" role="img">💼</span><span>Enterprise<br/><small>Custom Partnership</small></span></a>
        </div>
      </section>

      <section className={`${styles.section} ${styles.impactSection}`}>
        <h2><span aria-label="target" role="img">🎯</span> Your Impact in Action</h2>
        <div className={styles.impactGrid}>
          <div className={styles.impactCard}><div className={styles.impactAmount}>$5/month</div><div className={styles.impactResult}>= 2 hours of ADHD-focused development</div><div className={styles.impactDetail}>Powers new accessibility features</div></div>
          <div className={`${styles.impactCard} ${styles.impactCardFeatured}`}><div className={styles.impactAmount}>$15/month</div><div className={styles.impactResult}>= 1 week of dedicated coding time</div><div className={styles.impactDetail}>Funds major tool improvements</div></div>
          <div className={styles.impactCard}><div className={styles.impactAmount}>$50/month</div><div className={styles.impactResult}>= Full sprint of feature development</div><div className={styles.impactDetail}>Enables breakthrough innovations</div></div>
        </div>
      </section>

      <section id="support-tiers" className={`${styles.section} ${styles.fadeIn}`}>
        <h2><span aria-label="rocket" role="img">🚀</span> MONTHLY SUPPORT TIERS</h2>
        <p style={{ color: '#b0b0d0', maxWidth: 800, margin: '0 auto 30px', textAlign: 'center' }}>Choose your level of empire support and unlock exclusive rewards, early access, and direct impact on our development!</p>
        <div className={styles.tierGrid}>
          <div className={styles.tierCard}><div className={styles.tierBadge}>Warrior</div><h3><span aria-label="star" role="img">🌟</span> Focus Warrior</h3><div className={styles.tierPrice}>$5<span className={styles.tierPeriod}>/mo</span></div><ul className={styles.tierFeatures}><li><span aria-label="check mark" role="img">✅</span> Discord VIP role & channels</li><li><span aria-label="check mark" role="img">✅</span> Early access to new tools</li><li><span aria-label="check mark" role="img">✅</span> Monthly team updates</li><li><span aria-label="check mark" role="img">✅</span> BROski$ bonus rewards</li><li><span aria-label="check mark" role="img">✅</span> Community voting rights</li></ul><a href="https://patreon.com/hyperfocuszone" className={styles.donationBtn} target="_blank" rel="noopener noreferrer" aria-label="Join Focus Warrior tier on Patreon">Join Warriors</a></div>
          <div className={`${styles.tierCard} ${styles.tierCardFeatured}`}><div className={`${styles.tierBadge} ${styles.tierBadgePopular}`}>Most Popular</div><h3><span aria-label="diamond" role="img">💎</span> Elite Agent</h3><div className={styles.tierPrice}>$15<span className={styles.tierPeriod}>/mo</span></div><ul className={styles.tierFeatures}><li><span aria-label="check mark" role="img">✅</span> Everything in Focus Warrior</li><li><span aria-label="check mark" role="img">✅</span> Weekly 1:1 office hours</li><li><span aria-label="check mark" role="img">✅</span> Beta testing privileges</li><li><span aria-label="check mark" role="img">✅</span> Custom ADHD workflow sessions</li><li><span aria-label="check mark" role="img">✅</span> Direct feedback to Chief Lyndz</li><li><span aria-label="check mark" role="img">✅</span> Exclusive productivity templates</li></ul><a href="https://patreon.com/hyperfocuszone" className={`${styles.donationBtn} ${styles.donationBtnFeatured}`} target="_blank" rel="noopener noreferrer" aria-label="Join Elite Agent tier on Patreon">Join Elite Now!</a></div>
          <div className={styles.tierCard}><div className={styles.tierBadge}>Builder</div><h3><span aria-label="crown" role="img">👑</span> Empire Builder</h3><div className={styles.tierPrice}>$50<span className={styles.tierPeriod}>/mo</span></div><ul className={styles.tierFeatures}><li><span aria-label="check mark" role="img">✅</span> Everything in Elite Agent</li><li><span aria-label="check mark" role="img">✅</span> Monthly strategy calls</li><li><span aria-label="check mark" role="img">✅</span> Co-development opportunities</li><li><span aria-label="check mark" role="img">✅</span> Revenue sharing possibilities</li><li><span aria-label="check mark" role="img">✅</span> Your name in credits</li><li><span aria-label="check mark" role="img">✅</span> Early access to commercial tools</li></ul><a href="https://patreon.com/hyperfocuszone" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`} target="_blank" rel="noopener noreferrer" aria-label="Join Empire Builder tier on Patreon">Build Empire</a></div>
        </div>
      </section>

      <section className={`${styles.section} ${styles.testimonialsSection} ${styles.fadeIn}`}>
        <h2><span aria-label="speech bubble" role="img">💬</span> What Supporters Say</h2>
        <div className={styles.testimonialsGrid}>
          <blockquote className={styles.testimonial}><p>"Hyperfocus tools literally changed how I work with ADHD. Worth every penny!"</p><cite>– Alex K., Elite Agent</cite></blockquote>
          <blockquote className={styles.testimonial}><p>"Finally, productivity tools that actually understand neurodivergent minds."</p><cite>– Jamie R., Focus Warrior</cite></blockquote>
          <blockquote className={styles.testimonial}><p>"The community support alone is incredible. Best investment I've made."</p><cite>– Sam L., Empire Builder</cite></blockquote>
        </div>
      </section>

      <section className={`${styles.section} ${styles.fadeIn}`}>
        <h2><span aria-label="coffee cup" role="img">☕</span> ONE-TIME SUPPORT OPTIONS</h2>
        <div className={styles.supportGrid}>
          <div className={styles.supportCard}><h3><span aria-label="heart" role="img">💖</span> Buy Me A Coffee</h3><p>Quick and easy way to say thanks! Every coffee fuels late-night coding sessions and keeps the empire running.</p><div className={styles.buttonGroup}><a href="https://ko-fi.com/hyperfocuszone" className={styles.donationBtn} target="_blank" rel="noopener noreferrer"><span aria-label="coffee" role="img">☕</span> $3 Coffee</a><a href="https://ko-fi.com/hyperfocuszone" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`} target="_blank" rel="noopener noreferrer"><span aria-label="pizza" role="img">🍕</span> $10 Pizza</a></div></div>
          <div className={styles.supportCard}><h3><span aria-label="diamond" role="img">💎</span> PayPal Direct</h3><p>Send any amount directly via PayPal. Perfect for one-time appreciation or custom contribution amounts.</p><div className={styles.buttonGroup}><a href="https://paypal.me/WelshDog?locale.x=en_GB&country.x=GB" className={styles.donationBtn}><span aria-label="money bag" role="img">💰</span> Send PayPal</a><a href="https://www.patreon.com/u29188650" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`}><span aria-label="briefcase" role="img">💼</span> Business Inquiry</a></div></div>
          <div className={styles.supportCard}><h3><span aria-label="shopping cart" role="img">🛒</span> Digital Products</h3><p>Support us while getting awesome ADHD productivity tools, templates, and digital resources!</p><div className={styles.buttonGroup}><a href="https://etsy.com/shop/hyperfocuszoneGB" className={styles.donationBtn} target="_blank" rel="noopener noreferrer"><span aria-label="art palette" role="img">🎨</span> Etsy Shop</a><a href="https://tiktok.com/@hyperfocuszone/shop" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`} target="_blank" rel="noopener noreferrer"><span aria-label="musical note" role="img">🎵</span> TikTok Shop</a></div></div>
        </div>
      </section>

      <section className={`${styles.section} ${styles.fadeIn}`}>
        <h2><span aria-label="target" role="img">🎯</span> CURRENT FUNDING GOALS</h2>
        <div className={styles.fundingGoalContainer} style={{ textAlign: 'center' }}>
          <h3 style={{ color: '#00bfff', marginBottom: 20 }}><span aria-label="diamond" role="img">💎</span> Goal: $10,000/month - Infrastructure & Team Expansion</h3>
          <div className={styles.progressContainer}>
              <div 
                className={`${styles.progressBar} ${styles.fundingProgressBar}`} 
                style={{ width: `${fundingPercent}%` }}
                role="progressbar" 
                aria-valuenow={fundingPercent} 
                aria-valuemin={0} 
                aria-valuemax={100} 
                aria-label={`Funding progress: ${fundingPercent}% complete`}
              ></div>
          </div>
          <div className={styles.progressText}>${stats.fundingCurrent} of ${stats.fundingGoal} monthly goal reached ({fundingPercent}%)</div>
        </div>
        <div className={styles.goalsGrid}>
          <div className={styles.goalCardBlue}><h4 className={styles.goalCardTitleBlue}><span aria-label="fire" role="img">🔥</span> What Your Support Enables:</h4><ul className={styles.goalCardList}><li><span aria-label="check mark" role="img">✅</span> 24/7 server infrastructure</li><li><span aria-label="check mark" role="img">✅</span> Advanced AI model training</li><li><span aria-label="check mark" role="img">✅</span> Full-time development team</li><li><span aria-label="check mark" role="img">✅</span> Global content delivery</li><li><span aria-label="check mark" role="img">✅</span> Premium integrations</li></ul></div>
          <div className={styles.goalCardPurple}><h4 className={styles.goalCardTitlePurple}><span aria-label="rocket" role="img">🚀</span> Next Milestones:</h4><ul className={styles.goalCardList}><li><span aria-label="target" role="img">🎯</span> $15K/mo: Mobile app development</li><li><span aria-label="target" role="img">🎯</span> $25K/mo: AI research lab</li><li><span aria-label="target" role="img">🎯</span> $50K/mo: Global team expansion</li><li><span aria-label="target" role="img">🎯</span> $100K/mo: ADHD research institute</li></ul></div>
        </div>
      </section>

      <section id="contact" className={`${styles.section} ${styles.fadeIn}`}>
        <h2><span aria-label="speech bubble" role="img">💬</span> CONNECT & CONTRIBUTE</h2>
        <div className={styles.contactGrid}>
          <div className={styles.contactItem}><span className={styles.contactIcon} aria-label="speech bubble" role="img">💬</span><h4>Discord Community</h4><p>Join <span>{stats.discordCount > 0 ? stats.discordCount : '0+'}</span> ADHD warriors</p><a href="https://discord.gg/2fpxEsUyfa" className={styles.donationBtn} target="_blank" rel="noopener noreferrer">Join Discord</a></div>
          <div className={styles.contactItem}><span className={styles.contactIcon} aria-label="star" role="img">⭐</span><h4>GitHub Sponsor</h4><p>Support development directly</p><a href="https://github.com/sponsors/welshDog" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`} target="_blank" rel="noopener noreferrer">Sponsor</a></div>
          <div className={styles.contactItem}><span className={styles.contactIcon} aria-label="envelope" role="img">📧</span><h4>Business Inquiries</h4><p>Partnership opportunities</p><a href="mailto:business@hyperfocuszone.com" className={styles.donationBtn}>Contact</a></div>
          <div className={styles.contactItem}><span className={styles.contactIcon} aria-label="globe" role="img">🌐</span><h4>Website & Updates</h4><p>Latest news and announcements</p><a href="https://hyperfocuszone.com" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`} target="_blank" rel="noopener noreferrer">Visit Site</a></div>
        </div>
      </section>

      <footer className={styles.footer}>
        <h3><span aria-label="rocket" role="img">🚀</span> Thank You for Supporting the HYPERFOCUS Empire! <span aria-label="rocket" role="img">🚀</span></h3>
        <p style={{ color: '#b0b0d0', maxWidth: 600, margin: '0 auto' }}>Every contribution, no matter the size, helps us build better tools for ADHD minds worldwide. Together, we're creating a future where neurodivergent developers thrive!</p>
        <div style={{ marginTop: 30 }}>
          <a href="https://discord.gg/2fpxEsUyfa" className={styles.donationBtn} target="_blank" rel="noopener noreferrer"><span aria-label="speech bubble" role="img">💬</span> Discord</a>
          <a href="https://github.com/welshDog" className={`${styles.donationBtn} ${styles.donationBtnSecondary}`} target="_blank" rel="noopener noreferrer"><span aria-label="star" role="img">⭐</span> GitHub</a>
          <a href="mailto:SEND-ME.NFT@ud.me" className={styles.donationBtn}><span aria-label="envelope" role="img">📧</span> Contact</a>
        </div>
        <p style={{ marginTop: 30, color: '#666' }}>Built with <span aria-label="green heart" role="img">💚</span> by Lyndz and the HYPERFOCUS Community</p>
      </footer>
    </main>
  )
}
