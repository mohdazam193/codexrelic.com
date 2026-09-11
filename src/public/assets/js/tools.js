document.addEventListener('DOMContentLoaded', () => {
  // --- TABS LOGIC ---
  const tabBtns = document.querySelectorAll('.tool-tab-btn');
  const tabPanes = document.querySelectorAll('.tool-tab-pane');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Deactivate all
      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.style.background = 'transparent';
        b.style.color = 'var(--c-text-muted)';
        b.style.border = '1px solid transparent';
      });
      tabPanes.forEach(p => p.style.display = 'none');

      // Activate clicked
      btn.classList.add('active');
      btn.style.background = 'var(--c-accent-dim)';
      btn.style.color = 'var(--c-accent)';
      btn.style.border = '1px solid var(--c-accent)';
      
      const targetId = btn.getAttribute('data-target');
      document.getElementById(targetId).style.display = 'block';
    });
  });

  // --- CERTIFICATE DECODER LOGIC ---
  const decodeBtn = document.getElementById('decode-btn');
  const certInput = document.getElementById('cert-input');
  const resultsDiv = document.getElementById('cert-results');
  
  const els = {
    status: document.getElementById('cert-status'),
    subject: document.getElementById('cert-subject'),
    issuer: document.getElementById('cert-issuer'),
    validFrom: document.getElementById('cert-valid-from'),
    validTo: document.getElementById('cert-valid-to'),
    daysLeft: document.getElementById('cert-days-left'),
    serial: document.getElementById('cert-serial'),
    sigAlg: document.getElementById('cert-sig-alg'),
    sans: document.getElementById('cert-sans')
  };

  decodeBtn.addEventListener('click', () => {
    const pem = certInput.value.trim();
    if (!pem) return;

    try {
      if (typeof forge === 'undefined') {
        throw new Error('Parsing library not loaded. Please check your connection.');
      }

      // Convert PEM to Forge Certificate Object
      const cert = forge.pki.certificateFromPem(pem);

      // Parse Attributes (Subject/Issuer)
      const formatAttrs = (attrs) => {
        return attrs.map(a => `${a.shortName || a.name}=${a.value}`).join(', ');
      };

      els.subject.textContent = formatAttrs(cert.subject.attributes) || 'N/A';
      els.issuer.textContent = formatAttrs(cert.issuer.attributes) || 'N/A';

      // Parse Validity
      els.validFrom.textContent = cert.validity.notBefore.toUTCString();
      els.validTo.textContent = cert.validity.notAfter.toUTCString();
      
      const now = new Date();
      const daysLeft = Math.ceil((cert.validity.notAfter - now) / (1000 * 60 * 60 * 24));
      
      if (daysLeft < 0) {
        els.daysLeft.textContent = ` (Expired ${Math.abs(daysLeft)} days ago)`;
        els.daysLeft.style.color = 'var(--c-red)';
      } else if (daysLeft < 30) {
        els.daysLeft.textContent = ` (Expires in ${daysLeft} days)`;
        els.daysLeft.style.color = 'var(--c-amber)';
      } else {
        els.daysLeft.textContent = ` (Expires in ${daysLeft} days)`;
        els.daysLeft.style.color = 'var(--c-green)';
      }

      // Serial & Alg
      els.serial.textContent = cert.serialNumber || 'N/A';
      els.sigAlg.textContent = cert.siginfo ? cert.siginfo.algorithmOid : 'N/A';

      // Parse SANs
      let sansStr = 'None';
      const altNamesExt = cert.getExtension('subjectAltName');
      if (altNamesExt && altNamesExt.altNames) {
        sansStr = altNamesExt.altNames.map(san => san.value).join(', ');
      }
      els.sans.textContent = sansStr;

      els.status.textContent = 'VALID FORMAT';
      els.status.className = 'bento-status status-green';
      resultsDiv.style.display = 'block';

      // Scroll to results
      resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
      console.error(err);
      els.status.textContent = 'INVALID PEM';
      els.status.className = 'bento-status status-red';
      
      els.subject.textContent = err.message || 'Failed to parse certificate';
      els.issuer.textContent = '';
      els.validFrom.textContent = '';
      els.validTo.textContent = '';
      els.daysLeft.textContent = '';
      els.serial.textContent = '';
      els.sigAlg.textContent = '';
      els.sans.textContent = '';

      resultsDiv.style.display = 'block';
    }
  });
});
