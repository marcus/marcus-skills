# Avalara Page Patterns

Complete page templates and section patterns used across Avalara's web properties. Use these as blueprints when building marketing pages, product UIs, pricing pages, and developer portals.

## Table of Contents

- [Marketing Homepage](#marketing-homepage)
- [Product Page](#product-page)
- [Pricing Page](#pricing-page)
- [About Page](#about-page)
- [Developer Portal](#developer-portal)
- [Contact / Demo Request Page](#contact--demo-request-page)
- [Resource / Blog Listing](#resource--blog-listing)
- [Section Patterns](#section-patterns)
- [Responsive Behavior](#responsive-behavior)
- [SEO & Meta Patterns](#seo--meta-patterns)

---

## Marketing Homepage

### Structure

```
Header ─── logo + mega nav + search + "Request a demo"
│
Hero ───── H1 benefit headline
│          1–2 sentence subhead
│          Primary CTA: "Request a demo"
│          Optional secondary: "See how it works"
│
Stats ──── 43,000+ customers | 1,400+ integrations | 6M+ returns
│
Features ─ 3-column grid (light bg)
│          Each: icon + H3 title + description + "Learn more"
│
Dark ───── Teal (#025979) section
Section    H2 + body copy + CTA
│          Product screenshot or illustration
│
Social ─── Customer logos row
Proof      Testimonial quote + attribution
│          Awards: IDC MarketScape, Forrester TEI, Gallup
│
Products ─ Tab: "Purchase compliance" | "Sales compliance"
│          Product card grid
│
CTA ────── H2: "Ready to see what Avalara can do?"
Section    Primary CTA + secondary CTA
│
Footer ─── 5 columns + legal + locale selector
```

### Hero Section HTML

```html
<section class="hero">
  <div class="hero-inner">
    <div class="hero-content">
      <h1>Purpose-built for the systems you use — today and tomorrow</h1>
      <p class="hero-subtitle">
        Avalara automates tax compliance so you can focus on growing your business.
      </p>
      <div class="hero-actions">
        <a href="/demo" class="btn btn-primary btn-lg">Request a demo</a>
        <a href="/products" class="btn btn-secondary btn-lg">See how it works</a>
      </div>
    </div>
    <div class="hero-media">
      <!-- Product screenshot or illustration -->
    </div>
  </div>
</section>
```

### Hero CSS

```css
.hero {
  padding: var(--space-16) 0;
  background: var(--avalara-white);
}
.hero-inner {
  max-width: 1260px;
  margin: 0 auto;
  padding: 0 var(--space-4);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-8);
  align-items: center;
}
.hero h1 {
  font-size: var(--text-display);
  font-weight: var(--font-bold);
  line-height: var(--leading-tight);
  color: var(--avalara-black);
  margin-bottom: var(--space-3);
}
.hero-subtitle {
  font-size: var(--text-lg);
  color: var(--gray-600);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-4);
}
.hero-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
}

@media (max-width: 839px) {
  .hero-inner { grid-template-columns: 1fr; text-align: center; }
  .hero-actions { justify-content: center; }
  .hero h1 { font-size: var(--text-hero); }
}
```

---

## Product Page

### Structure

```
Header
│
Hero ───── Product name (H1) + description
│          "Request a demo" + "Start free trial"
│
Overview ─ 3-column feature grid
│          Each: icon + title + description
│
How It ─── Numbered steps (1, 2, 3)
Works      Step title + description + illustration
│
Use ────── 2-4 use case cards
Cases      Industry or scenario + benefit
│
Integration Grid of partner/platform logos
│
Proof ──── Stats: "90% faster" / "85% reduction" / etc.
│          Testimonial
│
CTA ────── "Ready to get started?" + demo form or CTA
│
Footer
```

### Product Feature Grid

```html
<section class="features-section">
  <div class="section-inner">
    <h2 class="section-heading">Why businesses choose AvaTax</h2>
    <div class="feature-grid">
      <div class="feature">
        <div class="feature-icon"><!-- icon --></div>
        <h3>Automated calculations</h3>
        <p>Real-time tax calculations across 12,000+ jurisdictions.</p>
      </div>
      <div class="feature">
        <div class="feature-icon"><!-- icon --></div>
        <h3>Seamless integration</h3>
        <p>Works with your existing ERP, ecommerce, and accounting platforms.</p>
      </div>
      <div class="feature">
        <div class="feature-icon"><!-- icon --></div>
        <h3>Always up to date</h3>
        <p>Tax content updated automatically as rules change.</p>
      </div>
    </div>
  </div>
</section>
```

```css
.features-section {
  padding: var(--space-16) 0;
  background: var(--avalara-white);
}
.section-inner {
  max-width: 1260px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}
.section-heading {
  font-size: var(--text-xxl);
  font-weight: var(--font-semibold);
  text-align: center;
  margin-bottom: var(--space-8);
  color: var(--avalara-black);
}
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
}
.feature {
  text-align: center;
  padding: var(--space-4);
}
.feature-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--space-2);
  color: var(--avalara-blue);
}
.feature h3 {
  font-size: var(--text-xl);
  margin-bottom: var(--space-1);
}
.feature p {
  color: var(--gray-600);
  line-height: var(--leading-relaxed);
}

@media (max-width: 839px) {
  .feature-grid { grid-template-columns: 1fr; }
}
```

### How It Works

```html
<section class="how-it-works section-subtle">
  <div class="section-inner">
    <h2 class="section-heading">How it works</h2>
    <div class="steps">
      <div class="step">
        <span class="step-number">1</span>
        <h3>Connect your systems</h3>
        <p>Integrate with 1,400+ pre-built connectors.</p>
      </div>
      <div class="step">
        <span class="step-number">2</span>
        <h3>Configure your rules</h3>
        <p>Set up tax profiles for your products and jurisdictions.</p>
      </div>
      <div class="step">
        <span class="step-number">3</span>
        <h3>Automate compliance</h3>
        <p>Tax is calculated, filed, and remitted automatically.</p>
      </div>
    </div>
  </div>
</section>
```

```css
.steps {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-6);
  counter-reset: step;
}
.step { text-align: center; }
.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--avalara-orange);
  color: var(--avalara-white);
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
  margin-bottom: var(--space-2);
}
```

---

## Pricing Page

### Structure

```
Header
│
Hero ───── "Avalara pricing is made to grow with your business"
│          "Discover how our pricing scales with you"
│
Tiers ──── 4 pricing cards:
│          New | Small | Midsize | Enterprise
│          Each: tier label, product list, CTA
│
Note ───── "25 states cover the cost for qualified sellers"
│
Individual Products with starting prices
Products   License Guidance: "as low as $119"
│          Registration: "$403 per location"
│
FAQ ────── Accordion: 6-8 questions
│
CTA ────── "Request a demo" / "Schedule a demo"
│
Footer
```

### Pricing Cards HTML

```html
<section class="pricing-section">
  <div class="section-inner">
    <h2 class="section-heading">Avalara pricing is made to grow with your business</h2>
    <p class="section-subtitle">Discover how our pricing scales with you, so you only pay for what you need.</p>

    <div class="pricing-grid">
      <div class="card card-pricing">
        <span class="card-tier">IDEAL FOR</span>
        <h3 class="card-title">New businesses</h3>
        <ul class="card-features">
          <li>AvaTax</li>
          <li>Basic returns</li>
        </ul>
        <a href="/demo" class="btn btn-primary">Get started</a>
      </div>

      <div class="card card-pricing">
        <span class="card-tier">IDEAL FOR</span>
        <h3 class="card-title">Small businesses</h3>
        <ul class="card-features">
          <li>AvaTax</li>
          <li>Returns</li>
          <li>ECM</li>
        </ul>
        <a href="/demo" class="btn btn-primary">Get pricing</a>
      </div>

      <div class="card card-pricing">
        <span class="card-tier">IDEAL FOR</span>
        <h3 class="card-title">Midsize businesses</h3>
        <ul class="card-features">
          <li>AvaTax</li>
          <li>Returns</li>
          <li>ECM</li>
          <li>Managed services</li>
        </ul>
        <a href="/demo" class="btn btn-primary">Get pricing</a>
      </div>

      <div class="card card-pricing card-pricing-featured">
        <span class="card-tier">IDEAL FOR</span>
        <h3 class="card-title">Enterprise businesses</h3>
        <ul class="card-features">
          <li>AvaTax</li>
          <li>Returns</li>
          <li>ECM</li>
          <li>E-Invoicing</li>
          <li>Custom integration</li>
          <li>Dedicated support</li>
        </ul>
        <a href="/demo" class="btn btn-primary">Contact sales</a>
      </div>
    </div>
  </div>
</section>
```

```css
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}
.card-pricing-featured {
  border-color: var(--avalara-blue);
  border-width: 2px;
}
@media (max-width: 839px) {
  .pricing-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 599px) {
  .pricing-grid { grid-template-columns: 1fr; }
}

.section-subtitle {
  text-align: center;
  font-size: var(--text-lg);
  color: var(--gray-600);
  margin-bottom: var(--space-8);
  max-width: 640px;
  margin-left: auto;
  margin-right: auto;
}
```

---

## About Page

### Structure

```
Header
│
Hero ───── "We're committed to making tax compliance less taxing"
│          Company mission statement
│
Stats ──── Avalara by the numbers
│          41,000+ customers | 1,400+ integrations | 6M+ returns | 31M+ docs
│
Values ─── OPAH FOCUS values grid
│          Optimism, Passion, Adaptability, Humility,
│          Fun, Ownership, Curiosity, Urgency, Simplicity
│
Awards ─── Gallup Exceptional Workplace
│          IDC MarketScape Leader
│          Industry recognitions
│
Leadership Leadership team grid
│
CTA ────── Careers, contact, demo
│
Footer
```

---

## Developer Portal

### Structure

```
Header ─── Dev-focused nav: Docs, API Reference, SDKs, Community
│          "Start free trial" CTA
│
Hero ───── "Agentic tax and compliance for global scale"
│          "Explore Avalara MCP servers" + "Start 90-day free trial"
│
Products ─ Card grid:
│          Calculation | Returns | ECM | E-Invoicing
│          Platforms | Licensing | Shared Services
│
Docs ───── Getting started guide
│          Code examples (with syntax highlighting)
│          API reference links
│
SDKs ───── Language-specific SDK cards (Python, Node, Java, C#, Ruby, PHP)
│
Community  Forum, GitHub, Stack Overflow links
│
Footer ─── Developer-specific footer
```

### Developer-specific styles

```css
.dev-hero {
  background: var(--avalara-teal);
  color: var(--avalara-white);
  padding: var(--space-12) 0;
}
.dev-hero h1 {
  font-size: var(--text-hero);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-3);
}

.code-block {
  background: var(--gray-900);
  color: #e5e7eb;
  border-radius: var(--radius-md);
  padding: var(--space-3);
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.6;
}

.sdk-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-3);
}
.sdk-card {
  background: var(--avalara-white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.sdk-card:hover { border-color: var(--avalara-blue); }
```

---

## Contact / Demo Request Page

### Structure

```
Header
│
Split ──── Left: benefit copy + trust signals
Layout     H1: "Let's solve your tax compliance challenges together"
│          Bullet points: what happens next
│          Stats or logos for credibility
│
│          Right: compact form
│          First name, Last name, Email, Company, Phone
│          "Get started" button
│          "Already a customer?" support link
│
Footer
```

### Split Layout CSS

```css
.contact-split {
  max-width: 1260px;
  margin: 0 auto;
  padding: var(--space-12) var(--space-4);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-12);
  align-items: start;
}
.contact-copy h1 {
  font-size: var(--text-hero);
  margin-bottom: var(--space-4);
}
.contact-steps {
  list-style: none;
  padding: 0;
}
.contact-steps li {
  padding: var(--space-2) 0;
  padding-left: var(--space-4);
  position: relative;
  color: var(--gray-600);
}
.contact-steps li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--avalara-orange);
  font-weight: var(--font-bold);
}

@media (max-width: 839px) {
  .contact-split {
    grid-template-columns: 1fr;
    gap: var(--space-6);
  }
}
```

---

## Resource / Blog Listing

### Structure

```
Header
│
Hero ───── "Resources" + category filter tabs
│
Filter ─── Type: Blog | Report | Webinar | Whitepaper
│          Topic filter dropdown
│
Grid ───── Resource cards (3 columns)
│          Each: type label, thumbnail, H3, excerpt, "Read" link
│
Pagination
│
Footer
```

---

## Section Patterns

### Alternating Light/Dark

```html
<section class="section-light"><!-- white bg, dark text --></section>
<section class="section-dark"><!-- teal bg, white text --></section>
<section class="section-subtle"><!-- gray-50 bg, dark text --></section>
```

### Customer Logos

```html
<section class="logos-section">
  <div class="section-inner">
    <p class="logos-heading">Trusted by 43,000+ businesses worldwide</p>
    <div class="logos-row">
      <img src="logo-1.svg" alt="Company 1" />
      <img src="logo-2.svg" alt="Company 2" />
      <img src="logo-3.svg" alt="Company 3" />
      <img src="logo-4.svg" alt="Company 4" />
      <img src="logo-5.svg" alt="Company 5" />
    </div>
  </div>
</section>
```

```css
.logos-section { padding: var(--space-8) 0; }
.logos-heading {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--gray-500);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin-bottom: var(--space-4);
}
.logos-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-8);
  flex-wrap: wrap;
}
.logos-row img {
  height: 32px;
  opacity: 0.5;
  filter: grayscale(1);
  transition: opacity var(--duration-fast);
}
.logos-row img:hover { opacity: 1; filter: none; }
```

### Final CTA Section

```html
<section class="cta-section section-dark">
  <div class="section-inner" style="text-align: center;">
    <h2>Ready to see what Avalara can do?</h2>
    <p>Get a personalized demo and see how Avalara fits your business.</p>
    <div class="hero-actions" style="justify-content: center; margin-top: var(--space-4);">
      <a href="/demo" class="btn btn-primary btn-lg">Request a demo</a>
      <a href="/contact" class="btn btn-secondary btn-lg" style="color: white; border-color: white;">Contact us</a>
    </div>
  </div>
</section>
```

### ROI / Impact Stats

```html
<section class="impact-section">
  <div class="section-inner">
    <h2 class="section-heading">The Avalara impact</h2>
    <p class="section-subtitle">Based on Forrester Total Economic Impact study</p>
    <div class="impact-grid">
      <div class="impact-stat">
        <span class="impact-number">90%</span>
        <span class="impact-label">increase in tax research efficiency</span>
      </div>
      <div class="impact-stat">
        <span class="impact-number">85%</span>
        <span class="impact-label">reduction in time on returns</span>
      </div>
      <div class="impact-stat">
        <span class="impact-number">50%</span>
        <span class="impact-label">reduction in exemption cert management</span>
      </div>
      <div class="impact-stat">
        <span class="impact-number">85%</span>
        <span class="impact-label">increase in audit prep efficiency</span>
      </div>
    </div>
  </div>
</section>
```

```css
.impact-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
}
.impact-stat { text-align: center; padding: var(--space-4); }
.impact-number {
  display: block;
  font-size: var(--text-display);
  font-weight: var(--font-bold);
  color: var(--avalara-blue);
}
.impact-label {
  font-size: var(--text-sm);
  color: var(--gray-600);
  margin-top: var(--space-1);
}

@media (max-width: 839px) {
  .impact-grid { grid-template-columns: repeat(2, 1fr); }
}
```

---

## Responsive Behavior

### Mobile-First Breakpoints

| Breakpoint | Layout Changes |
|-----------|---------------|
| `xs` (320–383) | Single column, stacked hero, full-width buttons |
| `sm` (384–599) | 1–2 columns, hamburger nav, stacked pricing cards |
| `md` (600–839) | 2 columns for cards, side-by-side form/copy |
| `lg` (840–1259) | Full multi-column, mega nav visible |
| `xl` (1260+) | Max-width container centered, full 12-column grid |

### Key Mobile Adaptations

- Hero: single column, centered text, stacked CTAs
- Nav: hamburger menu, full-width dropdown
- Cards: single column stack
- Stats: 2×2 grid instead of horizontal row
- Footer: single column, accordion-style sections
- Forms: full-width fields
- Tables: horizontal scroll with `overflow-x: auto`

---

## SEO & Meta Patterns

### Page Title Format

```
{Page Name} | Avalara
```

### Required Meta

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="[benefit-focused description, 150-160 chars]">
<link rel="icon" href="/favicon.ico">
```

### Favicon Requirements

Provide favicons for all contexts: browser tabs, macOS, iOS, Android, Windows.

### Structured Data

Use JSON-LD for Organization, Product, FAQ, and BreadcrumbList schemas where appropriate.

### Analytics

Marketing pages typically include Adobe Analytics and Google Analytics 4 via Google Tag Manager.
