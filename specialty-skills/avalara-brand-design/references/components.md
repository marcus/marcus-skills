# Avalara Component Library

HTML/CSS patterns for every standard Avalara UI component. Based on Skylab design system conventions (`s-` prefix for generic, `aui-` for Avalara-specific).

## Table of Contents

- [Buttons](#buttons)
- [Inputs & Forms](#inputs--forms)
- [Cards](#cards)
- [Alerts](#alerts)
- [Badges & Tags](#badges--tags)
- [Tables](#tables)
- [Modals / Dialogs](#modals--dialogs)
- [Tooltips](#tooltips)
- [Navigation](#navigation)
- [Tabs](#tabs)
- [Accordion / FAQ](#accordion--faq)
- [Stats Block](#stats-block)
- [Testimonial](#testimonial)
- [Footer](#footer)

---

## Buttons

### Variants

```html
<!-- Primary — orange, main CTA -->
<button class="btn btn-primary">Request a demo</button>

<!-- Secondary — outlined blue -->
<button class="btn btn-secondary">Learn more</button>

<!-- Tertiary — subtle, de-emphasized -->
<button class="btn btn-tertiary">Cancel</button>

<!-- Ghost — text-only, use sparingly -->
<button class="btn btn-ghost">Skip</button>

<!-- Ghost Blue — ghost with blue accent -->
<button class="btn btn-ghost-blue">View details</button>
```

### Sizes

```html
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
```

### States

```html
<button class="btn btn-primary" disabled>Disabled</button>
<button class="btn btn-primary btn-loading">
  <span class="spinner"></span> Loading...
</button>
```

### Icon Buttons

```html
<!-- Icon-only (must have aria-label + tooltip) -->
<button class="btn btn-icon" aria-label="Close">
  <svg><!-- icon --></svg>
</button>

<!-- Icon + text -->
<button class="btn btn-primary btn-icon-leading">
  <svg><!-- icon --></svg> Download
</button>
<button class="btn btn-secondary btn-icon-trailing">
  Next <svg><!-- arrow --></svg>
</button>
```

### CSS

```css
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-radius: var(--radius-sm);
  font-family: var(--font-sans);
  font-weight: var(--font-semibold);
  font-size: var(--text-md);
  padding: 12px 24px;
  cursor: pointer;
  transition: all var(--duration-fast) ease;
  text-decoration: none;
  border: none;
  line-height: 1;
}
.btn-sm { padding: 8px 16px; font-size: var(--text-sm); }
.btn-lg { padding: 16px 32px; font-size: var(--text-lg); }

.btn-primary {
  background: var(--avalara-orange);
  color: var(--avalara-white);
}
.btn-primary:hover { background: #e55d00; }
.btn-primary:active { background: #cc5200; }

.btn-secondary {
  background: transparent;
  color: var(--avalara-blue);
  border: 1px solid var(--avalara-blue);
}
.btn-secondary:hover {
  background: var(--color-blue-lightest);
}

.btn-tertiary {
  background: var(--gray-100);
  color: var(--gray-700);
  border: 1px solid var(--gray-200);
}
.btn-tertiary:hover { background: var(--gray-200); }

.btn-ghost {
  background: transparent;
  color: var(--avalara-blue);
  padding: 12px 16px;
}
.btn-ghost:hover { text-decoration: underline; }

.btn-ghost-blue {
  background: transparent;
  color: var(--avalara-blue);
}
.btn-ghost-blue:hover {
  background: var(--color-blue-lightest);
}

.btn:disabled, .btn[aria-disabled="true"] {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.btn-icon {
  padding: 8px;
  border-radius: var(--radius-sm);
}
```

---

## Inputs & Forms

### Text Input

```html
<div class="form-field">
  <label class="form-label" for="company">Company name <span class="required">*</span></label>
  <input type="text" id="company" class="form-input" placeholder="Enter company name" />
  <div class="form-hint">Legal business name</div>
</div>
```

### Validation States

```html
<!-- Success -->
<div class="form-field">
  <label class="form-label" for="email">Email</label>
  <input type="email" id="email" class="form-input input-success" value="user@example.com" />
  <div class="input-msg input-msg-success">Email verified</div>
</div>

<!-- Error -->
<div class="form-field">
  <label class="form-label" for="phone">Phone</label>
  <input type="tel" id="phone" class="form-input input-error" />
  <div class="input-msg input-msg-error">Phone number is required</div>
</div>

<!-- Warning -->
<div class="form-field">
  <label class="form-label" for="tax-id">Tax ID</label>
  <input type="text" id="tax-id" class="form-input input-warning" />
  <div class="input-msg input-msg-warning">Format may be incorrect</div>
</div>
```

### CSS

```css
.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: var(--space-3);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--gray-700);
}
.form-label .required { color: var(--color-red-medium); }

.form-input {
  padding: 10px 12px;
  border: 1px solid var(--gray-300);
  border-radius: var(--radius-sm);
  font-size: var(--text-md);
  font-family: var(--font-sans);
  color: var(--avalara-black);
  background: var(--avalara-white);
  transition: border-color var(--duration-fast);
}
.form-input:focus {
  outline: none;
  border-color: var(--avalara-blue);
  box-shadow: 0 0 0 3px rgba(5, 155, 210, 0.15);
}
.form-input::placeholder { color: var(--gray-400); }
.form-input:disabled {
  background: var(--gray-100);
  color: var(--gray-400);
  cursor: not-allowed;
}

.input-success { border-color: var(--color-green-medium); }
.input-warning { border-color: var(--color-yellow-medium); }
.input-error { border-color: var(--color-red-medium); }

.input-msg {
  font-size: var(--text-xs);
  margin-top: 2px;
}
.input-msg-success { color: var(--color-green-dark); }
.input-msg-warning { color: var(--color-yellow-darker); }
.input-msg-error { color: var(--color-red-dark); }

.form-hint {
  font-size: var(--text-xs);
  color: var(--gray-500);
}
```

### Form Layout

```html
<form class="avalara-form">
  <h2>Let's solve your tax compliance challenges together</h2>
  <p class="form-subtitle">Fill out this short form to connect with Avalara's tax solution experts.</p>

  <div class="form-grid">
    <div class="form-field"><!-- first name --></div>
    <div class="form-field"><!-- last name --></div>
    <div class="form-field form-field-full"><!-- email --></div>
    <div class="form-field form-field-full"><!-- company --></div>
  </div>

  <button type="submit" class="btn btn-primary btn-lg">Get started</button>
  <p class="form-footer">Already a customer? <a href="#">Get technical support</a></p>
</form>
```

```css
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2) var(--space-3);
}
.form-field-full { grid-column: 1 / -1; }
@media (max-width: 599px) {
  .form-grid { grid-template-columns: 1fr; }
}
```

---

## Cards

### Product Card

```html
<div class="card card-product">
  <h3 class="card-title">AvaTax</h3>
  <p class="card-desc">Automated tax calculation for transactions across the US and internationally.</p>
  <a href="#" class="card-link">Read more</a>
</div>
```

### Resource Card

```html
<div class="card card-resource">
  <span class="card-label">BLOG</span>
  <h3 class="card-title">2026 Sales Tax Changes You Should Know</h3>
  <p class="card-desc">Key legislative updates affecting compliance across 15 states.</p>
  <a href="#" class="card-link">Read the article</a>
</div>
```

### Pricing Card

```html
<div class="card card-pricing">
  <span class="card-tier">IDEAL FOR</span>
  <h3 class="card-title">Midsize businesses</h3>
  <ul class="card-features">
    <li>AvaTax</li>
    <li>Returns</li>
    <li>Exemption Certificate Management</li>
  </ul>
  <a href="#" class="btn btn-primary">Get pricing</a>
</div>
```

### CSS

```css
.card {
  background: var(--avalara-white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
  padding: var(--space-4);
  transition: box-shadow var(--duration-fast);
}
.card:hover { box-shadow: var(--shadow-md); }

.card-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--avalara-black);
  margin-bottom: var(--space-1);
}
.card-desc {
  font-size: var(--text-md);
  color: var(--gray-600);
  margin-bottom: var(--space-2);
  line-height: var(--leading-relaxed);
}
.card-link {
  color: var(--avalara-blue);
  font-weight: var(--font-semibold);
  text-decoration: underline;
}

.card-label {
  display: inline-block;
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  letter-spacing: var(--tracking-wider);
  text-transform: uppercase;
  color: var(--gray-500);
  margin-bottom: var(--space-1);
}

.card-tier {
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--avalara-orange);
  font-weight: var(--font-semibold);
}
.card-features {
  list-style: none;
  padding: 0;
  margin: var(--space-2) 0 var(--space-3);
}
.card-features li {
  padding: var(--space-1) 0;
  border-bottom: 1px solid var(--gray-100);
  font-size: var(--text-sm);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-3);
}
```

---

## Alerts

```html
<div class="alert alert-info" role="alert">
  <svg class="alert-icon"><!-- info icon --></svg>
  <div class="alert-content">
    <strong>New feature available.</strong> Check out automated returns filing.
  </div>
  <button class="alert-dismiss" aria-label="Dismiss">&times;</button>
</div>

<div class="alert alert-success" role="alert">
  <svg class="alert-icon"><!-- check icon --></svg>
  <div class="alert-content">Tax return submitted successfully.</div>
</div>

<div class="alert alert-warning" role="alert"><!-- ... --></div>
<div class="alert alert-error" role="alert"><!-- ... --></div>
```

```css
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-lg);
  font-size: var(--text-sm);
}
.alert-info    { background: var(--color-blue-lightest); color: var(--color-blue-dark); border: 1px solid var(--color-blue-light); }
.alert-success { background: var(--color-green-lighter); color: var(--color-green-darker); border: 1px solid var(--color-green-light); }
.alert-warning { background: var(--color-yellow-light);  color: var(--color-yellow-darker); border: 1px solid var(--color-yellow-medium); }
.alert-error   { background: var(--color-red-lighter);   color: var(--color-red-dark); border: 1px solid var(--color-red-medium); }

.alert-dismiss {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  margin-left: auto;
  opacity: 0.6;
}
.alert-dismiss:hover { opacity: 1; }
```

---

## Badges & Tags

```html
<!-- Badge (numeric count) -->
<span class="badge">3</span>

<!-- Tags -->
<span class="tag tag-default">Compliance</span>
<span class="tag tag-blue">Sales Tax</span>
<span class="tag tag-green">Active</span>
<span class="tag tag-yellow">Pending</span>
<span class="tag tag-red">Overdue</span>
<span class="tag tag-purple">Enterprise</span>
```

```css
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  background: var(--avalara-orange);
  color: var(--avalara-white);
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
}
.badge:empty { display: none; }

.tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
}
.tag-default { background: var(--gray-100); color: var(--gray-700); }
.tag-blue    { background: var(--color-blue-lightest); color: var(--color-blue-dark); }
.tag-green   { background: var(--color-green-lighter); color: var(--color-green-darker); }
.tag-yellow  { background: var(--color-yellow-light); color: var(--color-yellow-darker); }
.tag-red     { background: var(--color-red-lighter); color: var(--color-red-dark); }
.tag-purple  { background: var(--color-purple-lighter); color: var(--color-purple-dark); }
```

---

## Tables

```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>State</th>
        <th>Tax Rate</th>
        <th>Status</th>
        <th class="text-end">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>California</td>
        <td>7.25%</td>
        <td><span class="tag tag-green">Active</span></td>
        <td class="text-end"><a href="#" class="btn btn-ghost-blue btn-sm">View</a></td>
      </tr>
    </tbody>
  </table>
</div>
```

```css
.table-container {
  overflow-x: auto;
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-sm);
}
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}
.table th {
  text-align: left;
  padding: var(--space-2) var(--space-2);
  font-weight: var(--font-semibold);
  font-size: var(--text-xs);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  color: var(--gray-500);
  background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
}
.table td {
  padding: var(--space-2);
  border-bottom: 1px solid var(--gray-100);
  color: var(--avalara-black);
}
.table tr:hover td { background: var(--gray-50); }
.text-end { text-align: right; }
```

---

## Modals / Dialogs

```html
<div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <div class="modal-header">
      <h2 id="modal-title">Confirm submission</h2>
      <button class="modal-close" aria-label="Close">&times;</button>
    </div>
    <div class="modal-body">
      <p>Are you sure you want to submit this tax return?</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-tertiary">Cancel</button>
      <button class="btn btn-primary">Submit</button>
    </div>
  </div>
</div>
```

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}
.modal {
  background: var(--avalara-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xl);
  width: min(90vw, 520px);
  max-height: 85vh;
  overflow-y: auto;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--gray-200);
}
.modal-body { padding: var(--space-4); }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--gray-200);
}
.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--gray-400);
}
.modal-close:hover { color: var(--gray-700); }
```

---

## Tooltips

```html
<div class="tooltip-wrapper">
  <button class="btn btn-icon" aria-describedby="tip-1">
    <svg><!-- help icon --></svg>
  </button>
  <div class="tooltip" id="tip-1" role="tooltip">
    Tax nexus determines where you must collect sales tax.
  </div>
</div>
```

```css
.tooltip-wrapper { position: relative; display: inline-flex; }
.tooltip {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--gray-900);
  color: var(--avalara-white);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--duration-fast);
  z-index: 60;
}
.tooltip-wrapper:hover .tooltip,
.tooltip-wrapper:focus-within .tooltip {
  opacity: 1;
}
```

---

## Navigation

### Header

```html
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="header-logo" aria-label="Avalara home">
      <!-- Avalara logo SVG -->
    </a>
    <nav class="header-nav">
      <a href="/products" class="nav-link">Products</a>
      <a href="/solutions" class="nav-link">Solutions</a>
      <a href="/integrations" class="nav-link">Integrations</a>
      <a href="/resources" class="nav-link">Resources</a>
      <a href="/about" class="nav-link">About</a>
    </nav>
    <div class="header-actions">
      <a href="/demo" class="btn btn-primary">Request a demo</a>
    </div>
  </div>
</header>
```

```css
.site-header {
  background: var(--avalara-white);
  border-bottom: 1px solid var(--gray-200);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-inner {
  max-width: 1260px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 var(--space-4);
  height: 64px;
}
.header-logo { margin-right: var(--space-6); }
.header-nav {
  display: flex;
  gap: var(--space-4);
  flex: 1;
}
.nav-link {
  color: var(--gray-700);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  text-decoration: none;
  padding: 8px 0;
}
.nav-link:hover { color: var(--avalara-blue); }
```

---

## Tabs

```html
<div class="tabs">
  <button class="tab tab-active">Purchase compliance</button>
  <button class="tab">Sales compliance</button>
</div>
```

```css
.tabs {
  display: flex;
  border-bottom: 2px solid var(--gray-200);
  gap: var(--space-4);
}
.tab {
  background: none;
  border: none;
  padding: var(--space-2) 0;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--gray-500);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color var(--duration-fast);
}
.tab:hover { color: var(--avalara-black); }
.tab-active {
  color: var(--avalara-blue);
  border-bottom-color: var(--avalara-blue);
}
```

---

## Accordion / FAQ

```html
<div class="accordion">
  <details class="accordion-item">
    <summary class="accordion-trigger">How does Avalara pricing work?</summary>
    <div class="accordion-content">
      <p>Pricing scales with your business. You only pay for what you need.</p>
    </div>
  </details>
</div>
```

```css
.accordion-item {
  border-bottom: 1px solid var(--gray-200);
}
.accordion-trigger {
  padding: var(--space-3) 0;
  font-size: var(--text-md);
  font-weight: var(--font-semibold);
  color: var(--avalara-black);
  cursor: pointer;
  list-style: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.accordion-trigger::after {
  content: '+';
  font-size: 1.25rem;
  color: var(--gray-400);
  transition: transform var(--duration-fast);
}
details[open] .accordion-trigger::after {
  content: '−';
}
.accordion-content {
  padding: 0 0 var(--space-3);
  color: var(--gray-600);
  line-height: var(--leading-relaxed);
}
```

---

## Stats Block

```html
<section class="stats-section">
  <div class="stats-row">
    <div class="stat">
      <span class="stat-number">43,000+</span>
      <span class="stat-label">customers worldwide</span>
    </div>
    <div class="stat">
      <span class="stat-number">1,400+</span>
      <span class="stat-label">signed partner integrations</span>
    </div>
    <div class="stat">
      <span class="stat-number">6M+</span>
      <span class="stat-label">tax returns processed</span>
    </div>
    <div class="stat">
      <span class="stat-number">31M+</span>
      <span class="stat-label">documents managed</span>
    </div>
  </div>
</section>
```

```css
.stats-section {
  padding: var(--space-8) 0;
  background: var(--gray-50);
}
.stats-row {
  max-width: 1260px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  gap: var(--space-8);
  flex-wrap: wrap;
}
.stat { text-align: center; }
.stat-number {
  display: block;
  font-size: var(--text-hero);
  font-weight: var(--font-bold);
  color: var(--avalara-orange);
}
.stat-label {
  font-size: var(--text-sm);
  color: var(--gray-500);
  margin-top: var(--space-1);
}
```

---

## Testimonial

```html
<div class="testimonial">
  <blockquote class="testimonial-quote">
    "I knew we needed a software solution that was easy to use and could handle
    the complexity of tax across all 50 states."
  </blockquote>
  <div class="testimonial-attribution">
    <strong>Jason Heckel</strong>
    <span>Senior Director of Tax, Zillow</span>
  </div>
  <a href="#" class="card-link">Read the Zillow story</a>
</div>
```

```css
.testimonial {
  max-width: 640px;
  margin: 0 auto;
  text-align: center;
  padding: var(--space-8) var(--space-4);
}
.testimonial-quote {
  font-size: var(--text-xl);
  font-style: italic;
  color: var(--gray-700);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-4);
}
.testimonial-attribution {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: var(--space-2);
}
.testimonial-attribution strong {
  color: var(--avalara-black);
  font-size: var(--text-md);
}
.testimonial-attribution span {
  color: var(--gray-500);
  font-size: var(--text-sm);
}
```

---

## Footer

```html
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-columns">
      <div class="footer-col">
        <h4>About</h4>
        <ul>
          <li><a href="#">Sitemap</a></li>
          <li><a href="#">Locations</a></li>
          <li><a href="#">Press</a></li>
          <li><a href="#">Careers</a></li>
          <li><a href="#">Leadership</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Products & Services</h4>
        <ul>
          <li><a href="#">All products</a></li>
          <li><a href="#">AvaTax</a></li>
          <li><a href="#">Returns</a></li>
          <li><a href="#">ECM</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Integrations</h4>
        <ul>
          <li><a href="#">Browse all</a></li>
          <li><a href="#">Shopify</a></li>
          <li><a href="#">NetSuite</a></li>
          <li><a href="#">Stripe</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <ul>
          <li><a href="#">Tax rates</a></li>
          <li><a href="#">Calculator</a></li>
          <li><a href="#">Webinars</a></li>
          <li><a href="#">Support</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <p class="footer-phone">877-224-3650</p>
        <p class="footer-hours">Mon–Fri, 4:30 a.m.–4:30 p.m. PT</p>
      </div>
    </div>
    <div class="footer-legal">
      <div class="footer-links">
        <a href="#">Terms</a>
        <a href="#">Privacy</a>
        <a href="#">Cookies</a>
        <a href="#">Your Privacy Rights</a>
      </div>
      <div class="footer-locale">
        <select aria-label="Region">
          <option>English (US)</option>
          <option>English (UK)</option>
          <option>Deutsch</option>
          <option>Français</option>
          <option>Português</option>
        </select>
      </div>
    </div>
  </div>
</footer>
```

```css
.site-footer {
  background: var(--gray-900);
  color: var(--gray-300);
  padding: var(--space-8) 0 var(--space-4);
}
.footer-inner {
  max-width: 1260px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}
.footer-columns {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}
@media (max-width: 839px) {
  .footer-columns { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 599px) {
  .footer-columns { grid-template-columns: 1fr; }
}

.footer-col h4 {
  color: var(--avalara-white);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-2);
}
.footer-col ul { list-style: none; padding: 0; }
.footer-col li { margin-bottom: var(--space-1); }
.footer-col a {
  color: var(--gray-400);
  text-decoration: none;
  font-size: var(--text-sm);
}
.footer-col a:hover { color: var(--avalara-white); text-decoration: underline; }

.footer-phone {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--avalara-white);
}
.footer-hours { font-size: var(--text-xs); color: var(--gray-500); }

.footer-legal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-4);
  border-top: 1px solid var(--gray-700);
  font-size: var(--text-xs);
}
.footer-links { display: flex; gap: var(--space-3); }
.footer-links a { color: var(--gray-500); text-decoration: none; }
.footer-links a:hover { color: var(--gray-300); }
```
