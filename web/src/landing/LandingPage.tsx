import { useEffect } from 'react'
import './landing.css'
import { HowItWorks } from './HowItWorks'
import { Decisions, DemoPaths, Developers, FinalCta, Footer, Hero, Nav, Personas, Privacy } from './Sections'
import { SignalDemo } from './SignalDemo'

// Landing (#/), in the style of the 24/11 Next.js landing, Holst colours, Figma logo + fonts.
// The demo (#/demo), story (#/demo?story=1) and ops (#/ops) pages keep their own shell in App.tsx.
export default function LandingPage() {
  useEffect(() => {
    const html = document.documentElement
    html.dataset.page = 'landing'
    return () => { delete html.dataset.page }
  }, [])
  return (
    <div className="lp">
      <Nav />
      <main id="content" tabIndex={-1} style={{ outline: 'none' }}>
        <Hero />
        <SignalDemo />
        <DemoPaths />
        <Personas />
        <Decisions />
        <HowItWorks />
        <Privacy />
        <Developers />
        <FinalCta />
      </main>
      <Footer />
    </div>
  )
}
