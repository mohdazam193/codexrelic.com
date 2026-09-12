document.addEventListener('DOMContentLoaded', () => {
  const containerToday = document.getElementById('tech-news-container');
  const containerArchive = document.getElementById('tech-news-archive-container');
  const tabToday = document.getElementById('tab-today');
  const tabArchive = document.getElementById('tab-archive');

  const fallbackImages = [
    'https://images.unsplash.com/photo-1518770660439-4636190af475?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=700&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=700&auto=format&fit=crop&q=80'
  ];

  function renderNewsItem(item, index) {
    const rankNum = String(index + 1).padStart(2, '0');
    const fallbackImg = fallbackImages[index % fallbackImages.length];
    const imgSrc = item.image && item.image.startsWith('http') ? item.image : fallbackImg;
    
    const domainText = item.domain || 'YCOMBINATOR.COM';
    const faviconUrl = item.domain ? `https://www.google.com/s2/favicons?domain=${item.domain}&sz=64` : 'assets/images/logo-dark.png';

    const summaryText = item.summary || 'Click to view full story, source discussion and real-time updates on this trending technology topic.';

    const words = (item.summary || '').split(' ').length;
    const readTime = `${Math.max(2, Math.ceil(words / 35))} min read`;

    return `
      <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="news-card reveal visible">
        <div class="news-card-media">
          <span class="news-card-rank-overlay">#${rankNum}</span>
          <img src="${imgSrc}" alt="${item.title}" class="news-card-img" loading="lazy" onerror="this.onerror=null; this.src='${fallbackImg}';">
        </div>
        <div class="news-card-body">
          <div class="news-card-eyebrow">
            <span class="news-domain-tag">${domainText}</span>
            <div class="news-external-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            </div>
          </div>
          <h3 class="news-card-title">${item.title}</h3>
          <p class="news-card-summary">${summaryText}</p>
          <div class="news-card-footer">
            <div class="news-author-meta">
              <img src="${faviconUrl}" alt="" class="news-author-avatar" onerror="this.src='assets/images/logo-dark.png';">
              <span class="news-author-name">${domainText}</span>
            </div>
            <span class="news-read-time">${readTime}</span>
          </div>
        </div>
      </a>
    `;
  }

  function renderArchiveGroup(archiveGroup) {
    const itemsHtml = archiveGroup.news.map((item, i) => renderNewsItem(item, i)).join('');
    return `
      <div class="resume-section" style="margin-top: var(--sp-8);">
        <div class="resume-section-header">
          <h2 class="resume-section-title" style="font-size: 0.95rem;">${archiveGroup.date}</h2>
          <div class="resume-section-line"></div>
        </div>
        <div class="news-grid">
          ${itemsHtml}
        </div>
      </div>
    `;
  }

  async function loadData() {
    try {
      // Load Today
      const resToday = await fetch('/api/tech-news');
      const todayData = await resToday.json();
      
      if (todayData && todayData.length > 0) {
        containerToday.innerHTML = todayData.map((item, i) => renderNewsItem(item, i)).join('');
      } else {
        containerToday.innerHTML = `<p style="text-align:center; grid-column: 1 / -1; padding: 40px; color: var(--c-text-muted);">No news fetched yet for today. Check back soon!</p>`;
      }

      // Load Archive
      const resArchive = await fetch('/api/tech-news/archive');
      const archiveData = await resArchive.json();

      if (archiveData && archiveData.length > 0) {
        containerArchive.innerHTML = archiveData.map(group => renderArchiveGroup(group)).join('');
      } else {
        containerArchive.innerHTML = `<p style="text-align:center; padding: 40px; color: var(--c-text-muted);">No archived news available yet.</p>`;
      }

    } catch (e) {
      console.error("Error fetching tech news:", e);
      containerToday.innerHTML = `<p style="text-align:center; grid-column: 1 / -1; padding: 40px; color: var(--c-red);">Error loading feed. Please try again later.</p>`;
    }
  }

  // Tab switching logic
  function switchTab(isToday) {
    if (isToday) {
      tabToday.classList.add('active');
      tabToday.style.background = 'var(--c-accent-dim)';
      tabToday.style.borderColor = 'var(--c-accent)';
      tabToday.style.color = 'var(--c-accent)';

      tabArchive.classList.remove('active');
      tabArchive.style.background = '';
      tabArchive.style.borderColor = 'var(--c-border)';
      tabArchive.style.color = 'var(--c-text-secondary)';

      containerToday.style.display = 'grid';
      containerArchive.style.display = 'none';
    } else {
      tabArchive.classList.add('active');
      tabArchive.style.background = 'var(--c-accent-dim)';
      tabArchive.style.borderColor = 'var(--c-accent)';
      tabArchive.style.color = 'var(--c-accent)';

      tabToday.classList.remove('active');
      tabToday.style.background = '';
      tabToday.style.borderColor = 'var(--c-border)';
      tabToday.style.color = 'var(--c-text-secondary)';

      containerToday.style.display = 'none';
      containerArchive.style.display = 'block';
    }
  }

  tabToday.addEventListener('click', () => switchTab(true));
  tabArchive.addEventListener('click', () => switchTab(false));

  // Init
  loadData();
});

