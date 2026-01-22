---
layout: splash
title: "ServiceDispatch"
permalink: /
hidden: true
header:
  overlay_color: "#0d1b2a"
  overlay_filter: "0.8"
  overlay_image: /assets/img/hero-background.jpg
  actions:
    - label: "Launch Application"
      url: "/dashboard"
      btn_class: "btn--primary btn--large"
    - label: "Documentation"
      url: "/docs/"
      btn_class: "btn--light-outline btn--large"
excerpt: "Enterprise Service Management Platform<br/>Intelligent dispatch. Real-time tracking. Actionable analytics."

feature_row:
  - image_path: /assets/img/features/dispatch.svg
    alt: "Smart Dispatch"
    title: "Intelligent Dispatch"
    excerpt: "AI-powered technician routing optimizes every service call. Reduce travel time, increase first-time fix rates."
    url: "/docs/dispatch/"
    btn_label: "Learn More"
    btn_class: "btn--primary"

  - image_path: /assets/img/features/tickets.svg
    alt: "Ticket Management"
    title: "Ticket Management"
    excerpt: "End-to-end ticket lifecycle management with automated workflows, SLA tracking, and complete audit trails."
    url: "/docs/tickets/"
    btn_label: "Learn More"
    btn_class: "btn--primary"

  - image_path: /assets/img/features/analytics.svg
    alt: "Analytics"
    title: "Real-Time Analytics"
    excerpt: "Actionable insights from your service data. Track KPIs, identify trends, and optimize operations."
    url: "/docs/analytics/"
    btn_label: "Learn More"
    btn_class: "btn--primary"

feature_row2:
  - image_path: /assets/img/features/map.svg
    alt: "Geographic Intelligence"
    title: "Geographic Intelligence"
    excerpt: "Visualize your service territory with interactive maps. Track technician locations, optimize routes, and analyze coverage patterns."
    url: "/docs/maps/"
    btn_label: "Explore"
    btn_class: "btn--primary"

  - image_path: /assets/img/features/parts.svg
    alt: "Parts Management"
    title: "Parts & Inventory"
    excerpt: "Integrated parts lookup across 8+ suppliers. AI-powered diagnosis recommendations based on historical data."
    url: "/docs/parts/"
    btn_label: "Explore"
    btn_class: "btn--primary"

  - image_path: /assets/img/features/integration.svg
    alt: "Integration"
    title: "Seamless Integration"
    excerpt: "Connect with ServicePower, Lotus systems, and more. RESTful APIs and webhook support for custom integrations."
    url: "/docs/integration/"
    btn_label: "Explore"
    btn_class: "btn--primary"
---

{% include feature_row id="feature_row" %}

---

## Platform Overview
{: .text-center}

ServiceDispatch is an enterprise-grade service management platform designed for modern field service operations. Built with scalability, reliability, and user experience at its core.
{: .text-center}

{% include feature_row id="feature_row2" %}

---

## Key Metrics
{: .text-center}

<div class="metrics-grid" markdown="0">
  <div class="metric-card">
    <div class="metric-value">8,900+</div>
    <div class="metric-label">Parts Tracked</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">125+</div>
    <div class="metric-label">Service Locations</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">99.9%</div>
    <div class="metric-label">Uptime SLA</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">&lt;1s</div>
    <div class="metric-label">Response Time</div>
  </div>
</div>

---

## Integration Ecosystem
{: .text-center}

<div class="integration-logos" markdown="0">
  <div class="integration-item">
    <img src="/assets/img/logos/servicepower.svg" alt="ServicePower">
    <span>ServicePower</span>
  </div>
  <div class="integration-item">
    <img src="/assets/img/logos/lotus.svg" alt="Lotus">
    <span>Lotus Approach</span>
  </div>
  <div class="integration-item">
    <img src="/assets/img/logos/openstreetmap.svg" alt="OpenStreetMap">
    <span>OpenStreetMap</span>
  </div>
  <div class="integration-item">
    <img src="/assets/img/logos/chartjs.svg" alt="Chart.js">
    <span>Chart.js</span>
  </div>
</div>

---

## Quick Start
{: .text-center}

Get up and running in minutes with our streamlined setup process.
{: .text-center}

```bash
# Clone the repository
git clone https://github.com/organization/servicedispatch.git
cd servicedispatch

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Launch application
flask run
```

[View Full Installation Guide](/docs/getting-started/){: .btn .btn--primary .btn--large}
{: .text-center}

---

## What Our Users Say
{: .text-center}

> "ServiceDispatch transformed our field operations. Response times are down 40% and customer satisfaction is at an all-time high."
>
> **-- Operations Manager, Enterprise Client**

> "The analytics dashboard gives us insights we never had before. We can now make data-driven decisions about staffing and routing."
>
> **-- Service Director, Regional Provider**

---

## Ready to Get Started?
{: .text-center}

Experience the power of intelligent service management.
{: .text-center}

[Launch Application](/dashboard){: .btn .btn--primary .btn--x-large}
[Request Demo](/demo){: .btn .btn--light-outline .btn--x-large}
[Contact Sales](/contact){: .btn .btn--light-outline .btn--x-large}
{: .text-center}

<style>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  padding: 2rem 0;
  max-width: 1000px;
  margin: 0 auto;
}

.metric-card {
  background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-4px);
}

.metric-value {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.metric-label {
  font-size: 1rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.integration-logos {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 3rem;
  padding: 2rem 0;
}

.integration-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.integration-item img {
  height: 48px;
  width: auto;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.integration-item:hover img {
  opacity: 1;
}

.integration-item span {
  font-size: 0.875rem;
  color: #666;
}

.btn--x-large {
  padding: 1rem 2.5rem;
  font-size: 1.125rem;
}

.btn--light-outline {
  border: 2px solid #1a365d;
  color: #1a365d;
  background: transparent;
}

.btn--light-outline:hover {
  background: #1a365d;
  color: #fff;
}
</style>
