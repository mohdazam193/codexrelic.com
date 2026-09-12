document.addEventListener('DOMContentLoaded', () => {
  const containerToday = document.getElementById('tech-news-container');
  const containerArchive = document.getElementById('tech-news-archive-container');
  const tabToday = document.getElementById('tab-today');
  const tabArchive = document.getElementById('tab-archive');

  function renderNewsItem(item, index) {
    const rankNum = String(index + 1).padStart(2, '0');
    const domainBadge = item.domain 
      ? `<span class="news-domain-tag">${item.domain}</span>` 
      : '';
    
    const summaryHtml = item.summary 
      ? `<p class="news-card-summary">${item.summary}</p>` 
      : '';

    const dateStr = item.published ? new Date(item.published).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' }) : '';

    return `
      <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="news-card reveal visible">
        <div class="news-card-header">
          <span class="news-rank-badge">#${rankNum}</span>
          ${domainBadge}
          <div class="news-external-icon">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </div>
        </div>
        <h3 class="news-card-title">${item.title}</h3>
        ${summaryHtml}
        <div class="news-card-footer">
          <span>${dateStr}</span>
          <span class="news-read-link">Read Story &rarr;</span>
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

