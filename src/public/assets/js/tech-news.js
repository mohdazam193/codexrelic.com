document.addEventListener('DOMContentLoaded', () => {
  const containerToday = document.getElementById('tech-news-container');
  const containerArchive = document.getElementById('tech-news-archive-container');
  const tabToday = document.getElementById('tab-today');
  const tabArchive = document.getElementById('tab-archive');

  function renderNewsItem(item, index) {
    return `
      <a href="${item.link}" target="_blank" class="timeline-card reveal visible" style="display: flex; gap: var(--sp-4); text-decoration: none; align-items: center; cursor: pointer; flex-direction: row;">
        <div style="font-family: var(--font-display); font-size: 2rem; font-weight: 700; color: var(--c-accent); opacity: 0.5; width: 40px; text-align: center; flex-shrink: 0;">
          ${index + 1}
        </div>
        <div style="flex: 1;">
          <h3 style="font-size: 1.1rem; color: var(--c-text); margin-bottom: 4px;">${item.title}</h3>
          <p style="font-size: 0.8rem; color: var(--c-text-muted); font-family: var(--font-mono);">${new Date(item.published).toLocaleString()}</p>
        </div>
        <div style="flex-shrink: 0;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--c-accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.5;"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
        </div>
      </a>
    `;
  }

  function renderArchiveGroup(archiveGroup) {
    const itemsHtml = archiveGroup.news.map((item, i) => renderNewsItem(item, i)).join('');
    return `
      <div class="resume-section" style="margin-top: var(--sp-8);">
        <div class="resume-section-header">
          <h2 class="resume-section-title" style="font-size: 0.9rem;">${archiveGroup.date}</h2>
          <div class="resume-section-line"></div>
        </div>
        <div style="display: flex; flex-direction: column; gap: var(--sp-4);">
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
        containerToday.innerHTML = `<p style="text-align:center; padding: 40px; color: var(--c-text-muted);">No news fetched yet for today. Check back soon!</p>`;
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
      containerToday.innerHTML = `<p style="text-align:center; padding: 40px; color: var(--c-red);">Error loading feed. Please try again later.</p>`;
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

      containerToday.style.display = 'flex';
      containerToday.style.flexDirection = 'column';
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
