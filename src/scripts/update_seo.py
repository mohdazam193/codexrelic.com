"""
update_seo.py — Comprehensive SEO update for all codexrelic.com pages.

Fixes:
1. Corrects wrong meta tags on tech-news.html and tools.html
2. Adds keywords meta tags to all pages
3. Adds theme-color meta tag
4. Adds favicon link tags
5. Adds JSON-LD structured data (schema.org Person + WebSite)
6. Updates sitemap.xml with missing pages
"""
import re
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# ─── SEO data for each page ───
SEO_DATA = {
    "index.html": {
        "title": "Mohd Azam · SRE &amp; Platform Engineer",
        "description": "Mohd Azam — Site Reliability Engineer &amp; Platform Engineer with 6+ years building production-grade infrastructure for enterprise SaaS. Specializing in Kubernetes, observability, and DevSecOps.",
        "og_title": "Mohd Azam · SRE &amp; Platform Engineer",
        "og_description": "Site Reliability Engineer with 6+ years in multi-tenant SaaS. Building production-grade platforms on Kubernetes, Terraform, and cloud-native observability stacks.",
        "canonical": "https://codexrelic.com/",
        "keywords": "SRE, Site Reliability Engineer, Platform Engineer, DevOps, Kubernetes, Terraform, Observability, Mohd Azam, codexrelic",
    },
    "about.html": {
        "title": "About — Mohd Azam · codexrelic.com",
        "description": "Learn about Mohd Azam — SRE and Platform Engineer based in Hyderabad, India. Background in multi-tenant SaaS, cloud infrastructure, and DevSecOps.",
        "og_title": "About — Mohd Azam · codexrelic.com",
        "og_description": "Learn about Mohd Azam — SRE and Platform Engineer based in Hyderabad. Building reliable systems at scale.",
        "canonical": "https://codexrelic.com/about.html",
        "keywords": "Mohd Azam, About, SRE, Platform Engineer, Hyderabad, DevOps Engineer, Cloud Infrastructure",
    },
    "resume.html": {
        "title": "Resume — Mohd Azam · codexrelic.com",
        "description": "Resume of Mohd Azam — DevOps Engineer, SRE &amp; Platform Engineer with 6+ years in multi-tenant SaaS at Mitratech. Skills in Kubernetes, Terraform, CI/CD, and observability.",
        "og_title": "Resume — Mohd Azam · codexrelic.com",
        "og_description": "DevOps Engineer · SRE · Platform Engineering — 6+ years in multi-tenant SaaS, Kubernetes, Terraform, and cloud-native observability.",
        "canonical": "https://codexrelic.com/resume.html",
        "keywords": "Resume, CV, Mohd Azam, DevOps Engineer, SRE, Platform Engineer, Kubernetes, Terraform, Mitratech, Hyderabad",
    },
    "projects.html": {
        "title": "Projects — Mohd Azam · codexrelic.com",
        "description": "SRE &amp; Platform Engineering case studies by Mohd Azam — open-source projects, infrastructure automation, and DevSecOps tooling.",
        "og_title": "Projects — Mohd Azam · codexrelic.com",
        "og_description": "Explore SRE case studies, open-source projects, and infrastructure automation by Mohd Azam.",
        "canonical": "https://codexrelic.com/projects.html",
        "keywords": "Projects, SRE Projects, DevOps Tools, Open Source, Infrastructure Automation, Mohd Azam",
    },
    "blog.html": {
        "title": "Learning Journal — Mohd Azam · codexrelic.com",
        "description": "Technical write-ups on SRE, Kubernetes, observability, and platform engineering. Notes from KubeCon, AWS summits, and real-world incident postmortems.",
        "og_title": "Learning Journal — Mohd Azam · codexrelic.com",
        "og_description": "Technical SRE write-ups, Kubernetes deep-dives, and conference notes from KubeCon and AWS summits.",
        "canonical": "https://codexrelic.com/blog.html",
        "keywords": "Blog, SRE Blog, Kubernetes, Observability, Platform Engineering, KubeCon, DevOps, Mohd Azam",
    },
    "tech-news.html": {
        "title": "Tech News — Daily Top 10 · codexrelic.com",
        "description": "Daily top 10 tech stories curated from Hacker News, refreshed every 3 hours. Stay updated on the latest in technology, startups, and engineering.",
        "og_title": "Tech News — Daily Top 10 · codexrelic.com",
        "og_description": "Daily top 10 tech stories from Hacker News, auto-refreshed every 3 hours. Curated by codexrelic.com.",
        "canonical": "https://codexrelic.com/tech-news.html",
        "keywords": "Tech News, Hacker News, Top 10, Daily Tech, Technology News, Startups, Engineering News",
    },
    "tools.html": {
        "title": "SRE Tools — Certificate Decoder · codexrelic.com",
        "description": "Free online SRE tools — decode X.509 SSL/TLS certificates instantly. View Common Name, SANs, validity, serial number, and signature algorithm.",
        "og_title": "SRE Tools — Certificate Decoder · codexrelic.com",
        "og_description": "Free online X.509 certificate decoder — instantly view CN, SANs, expiry, serial number and more.",
        "canonical": "https://codexrelic.com/tools.html",
        "keywords": "Certificate Decoder, SSL Certificate, TLS, X.509, PEM Decoder, SRE Tools, Online Tools, Mohd Azam",
    },
    "movies.html": {
        "title": "Cinema Logs — Mohd Azam · codexrelic.com",
        "description": "Curated movie catalog with personal reviews — sci-fi, philosophy, and classic cinema recommendations by Mohd Azam.",
        "og_title": "Cinema Logs — Mohd Azam · codexrelic.com",
        "og_description": "Personal movie reviews and curated picks across sci-fi, philosophy, and classic cinema.",
        "canonical": "https://codexrelic.com/movies.html",
        "keywords": "Movies, Cinema, Movie Reviews, Sci-Fi Movies, Philosophy Films, Mohd Azam, Film Recommendations",
    },
    "community.html": {
        "title": "Community Hub — Mohd Azam · codexrelic.com",
        "description": "Join the CodexRelic community hub — connect with DevOps engineers and SREs. Discord, open-source contributions, and knowledge sharing.",
        "og_title": "Community Hub — Mohd Azam · codexrelic.com",
        "og_description": "Join the CodexRelic community — connect with DevOps engineers, SREs, and open-source contributors.",
        "canonical": "https://codexrelic.com/community.html",
        "keywords": "Community, DevOps Community, SRE Community, Discord, Open Source, CodexRelic, Mohd Azam",
    },
    "contact.html": {
        "title": "Contact — Mohd Azam · codexrelic.com",
        "description": "Contact Mohd Azam — reach out for SRE consulting, DevOps collaboration, or platform engineering opportunities. Based in Hyderabad, India.",
        "og_title": "Contact — Mohd Azam · codexrelic.com",
        "og_description": "Reach out to Mohd Azam for SRE consulting, DevOps collaboration, or career opportunities.",
        "canonical": "https://codexrelic.com/contact.html",
        "keywords": "Contact, Mohd Azam, SRE Consulting, DevOps, Hire, Platform Engineer, Hyderabad",
    },
}

# JSON-LD structured data for the home page
JSONLD_HOME = """\n  <!-- Structured Data (JSON-LD) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "codexrelic.com",
    "url": "https://codexrelic.com/",
    "description": "Portfolio and engineering hub of Mohd Azam — SRE & Platform Engineer",
    "author": {
      "@type": "Person",
      "name": "Mohd Azam",
      "jobTitle": "Site Reliability Engineer & Platform Engineer",
      "url": "https://codexrelic.com/",
      "sameAs": [
        "https://linkedin.com/in/mohdazam193",
        "https://github.com/mohdazam193"
      ],
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Hyderabad",
        "addressCountry": "IN"
      }
    }
  }
  </script>"""

# Extra meta tags to inject into <head> (after viewport)
EXTRA_META = """
  <meta name="theme-color" content="#07151e">
  <link rel="icon" type="image/png" href="assets/images/logo-dark.png">"""


for filename, seo in SEO_DATA.items():
    filepath = os.path.join(PUBLIC_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[⚠️] Skipping {filename} — not found")
        continue

    with open(filepath, "r") as f:
        content = f.read()

    # 1. Fix <title>
    content = re.sub(
        r'<title>.*?</title>',
        f'<title>{seo["title"]}</title>',
        content, count=1
    )

    # 2. Fix meta description
    content = re.sub(
        r'<meta name="description" content=".*?">',
        f'<meta name="description" content="{seo["description"]}">',
        content, count=1
    )

    # 3. Fix canonical
    content = re.sub(
        r'<link rel="canonical" href=".*?">',
        f'<link rel="canonical" href="{seo["canonical"]}">',
        content, count=1
    )

    # 4. Fix OG tags
    content = re.sub(
        r'<meta property="og:url" content=".*?">',
        f'<meta property="og:url" content="{seo["canonical"]}">',
        content, count=1
    )
    content = re.sub(
        r'<meta property="og:title" content=".*?">',
        f'<meta property="og:title" content="{seo["og_title"]}">',
        content, count=1
    )
    content = re.sub(
        r'<meta property="og:description" content=".*?">',
        f'<meta property="og:description" content="{seo["og_description"]}">',
        content, count=1
    )

    # 5. Fix Twitter tags
    content = re.sub(
        r'<meta name="twitter:url" content=".*?">',
        f'<meta name="twitter:url" content="{seo["canonical"]}">',
        content, count=1
    )
    content = re.sub(
        r'<meta name="twitter:title" content=".*?">',
        f'<meta name="twitter:title" content="{seo["og_title"]}">',
        content, count=1
    )
    content = re.sub(
        r'<meta name="twitter:description" content=".*?">',
        f'<meta name="twitter:description" content="{seo["og_description"]}">',
        content, count=1
    )

    # 6. Add keywords meta tag (if not already present)
    if 'name="keywords"' not in content:
        content = content.replace(
            '<meta name="author"',
            f'<meta name="keywords" content="{seo["keywords"]}">\n  <meta name="author"'
        )

    # 7. Add theme-color + favicon (if not present)
    if 'theme-color' not in content:
        content = content.replace(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">' + EXTRA_META
        )

    # 8. Add JSON-LD structured data to home page only
    if filename == "index.html" and 'application/ld+json' not in content:
        content = content.replace('</head>', JSONLD_HOME + '\n</head>')

    with open(filepath, "w") as f:
        f.write(content)

    print(f"[✅] Updated SEO for {filename}")


# ─── Update sitemap.xml ───
today = datetime.utcnow().strftime("%Y-%m-%d")
sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://codexrelic.com/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/about.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/resume.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/projects.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/blog.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/tech-news.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/tools.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/movies.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/community.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://codexrelic.com/contact.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>yearly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>
"""

sitemap_path = os.path.join(PUBLIC_DIR, "sitemap.xml")
with open(sitemap_path, "w") as f:
    f.write(sitemap)
print(f"\n[✅] Updated sitemap.xml with all 10 pages + lastmod dates")

print("\n🎉 SEO update complete!")
