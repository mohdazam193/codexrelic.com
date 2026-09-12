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
    cn: document.getElementById('cert-cn'),
    sans: document.getElementById('cert-sans'),
    org: document.getElementById('cert-org'),
    ou: document.getElementById('cert-ou'),
    locality: document.getElementById('cert-locality'),
    state: document.getElementById('cert-state'),
    country: document.getElementById('cert-country'),
    subject: document.getElementById('cert-subject'),
    issuer: document.getElementById('cert-issuer'),
    validFrom: document.getElementById('cert-valid-from'),
    validTo: document.getElementById('cert-valid-to'),
    daysLeft: document.getElementById('cert-days-left'),
    serial: document.getElementById('cert-serial'),
    sigAlg: document.getElementById('cert-sig-alg'),
  };

  // Helper: get a specific attribute value from cert subject/issuer by shortName
  function getAttr(attrs, shortName) {
    const attr = attrs.find(a => a.shortName === shortName || a.name === shortName);
    return attr ? attr.value : '';
  }

  // Helper: format date as "Month Day, Year"
  function formatDate(date) {
    const months = ['January','February','March','April','May','June',
                    'July','August','September','October','November','December'];
    return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
  }

  // Helper: format all attributes into a single DN string
  function formatDN(attrs) {
    return attrs.map(a => `${a.shortName || a.name}=${a.value}`).join(', ');
  }

  // OID to human-readable signature algorithm mapping
  const sigAlgNames = {
    '1.2.840.113549.1.1.5': 'SHA-1 with RSA (sha1WithRSAEncryption)',
    '1.2.840.113549.1.1.11': 'SHA-256 with RSA (sha256WithRSAEncryption)',
    '1.2.840.113549.1.1.12': 'SHA-384 with RSA (sha384WithRSAEncryption)',
    '1.2.840.113549.1.1.13': 'SHA-512 with RSA (sha512WithRSAEncryption)',
    '1.2.840.10045.4.3.2': 'ECDSA with SHA-256',
    '1.2.840.10045.4.3.3': 'ECDSA with SHA-384',
    '1.2.840.10045.4.3.4': 'ECDSA with SHA-512',
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
      const subjectAttrs = cert.subject.attributes;
      const issuerAttrs = cert.issuer.attributes;

      // Individual subject fields
      els.cn.textContent = getAttr(subjectAttrs, 'CN') || 'N/A';
      els.org.textContent = getAttr(subjectAttrs, 'O') || '';
      els.ou.textContent = getAttr(subjectAttrs, 'OU') || '';
      els.locality.textContent = getAttr(subjectAttrs, 'L') || '';
      els.state.textContent = getAttr(subjectAttrs, 'ST') || '';
      els.country.textContent = getAttr(subjectAttrs, 'C') || '';

      // Full DN strings
      els.subject.textContent = formatDN(subjectAttrs) || 'N/A';
      els.issuer.textContent = formatDN(issuerAttrs) || 'N/A';

      // Parse SANs
      let sansStr = '';
      const altNamesExt = cert.getExtension('subjectAltName');
      if (altNamesExt && altNamesExt.altNames) {
        sansStr = altNamesExt.altNames.map(san => san.value).join(', ');
      }
      els.sans.textContent = sansStr;

      // Parse Validity with human-readable format
      els.validFrom.textContent = formatDate(cert.validity.notBefore);
      els.validTo.textContent = formatDate(cert.validity.notAfter);
      
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

      // Serial Number
      els.serial.textContent = cert.serialNumber || 'N/A';

      // Signature Algorithm — map OID to readable name
      const oid = cert.siginfo ? cert.siginfo.algorithmOid : '';
      els.sigAlg.textContent = sigAlgNames[oid] || oid || 'N/A';

      els.status.textContent = 'VALID FORMAT';
      els.status.className = 'bento-status status-green';
      resultsDiv.style.display = 'block';

      // Scroll to results
      resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (err) {
      console.error(err);
      els.status.textContent = 'INVALID PEM';
      els.status.className = 'bento-status status-red';
      
      els.cn.textContent = err.message || 'Failed to parse certificate';
      els.sans.textContent = '';
      els.org.textContent = '';
      els.ou.textContent = '';
      els.locality.textContent = '';
      els.state.textContent = '';
      els.country.textContent = '';
      els.subject.textContent = '';
      els.issuer.textContent = '';
      els.validFrom.textContent = '';
      els.validTo.textContent = '';
      els.daysLeft.textContent = '';
      els.serial.textContent = '';
      els.sigAlg.textContent = '';

      resultsDiv.style.display = 'block';
    }
  });
});
