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

  // --- MACHINE KEY GENERATOR LOGIC ---
  const mkPresetBtns = document.querySelectorAll('#mk-preset-group .tool-pill-btn');
  const mkValBtns = document.querySelectorAll('#mk-val-group .tool-pill-btn');
  const mkDecBtns = document.querySelectorAll('#mk-dec-group .tool-pill-btn');
  
  const mkValInfo = document.getElementById('mk-val-info');
  const mkDecInfo = document.getElementById('mk-dec-info');
  const mkGenerateBtn = document.getElementById('mk-generate-btn');
  const mkClearBtn = document.getElementById('mk-clear-btn');
  
  const mkResultsPanel = document.getElementById('mk-results-panel');
  const mkXmlOutput = document.getElementById('mk-xml-output');
  const mkValKeyBox = document.getElementById('mk-val-key-box');
  const mkDecKeyBox = document.getElementById('mk-dec-key-box');
  const mkValKeyCount = document.getElementById('mk-val-key-count');
  const mkDecKeyCount = document.getElementById('mk-dec-key-count');

  const mkCopyXmlBtn = document.getElementById('mk-copy-xml-btn');
  const mkCopyValBtn = document.getElementById('mk-copy-val-btn');
  const mkCopyDecBtn = document.getElementById('mk-copy-dec-btn');

  let selectedValidation = 'HMACSHA256';
  let selectedValBytes = 64;
  let selectedDecryption = 'AES';
  let selectedDecBytes = 32;
  let currentPreset = 'net45';

  // Helper: Secure Random Hex Generator (100% In-Browser Cryptography)
  function generateSecureHex(byteLength) {
    const bytes = new Uint8Array(byteLength);
    window.crypto.getRandomValues(bytes);
    let hex = '';
    for (let i = 0; i < bytes.length; i++) {
      hex += bytes[i].toString(16).padStart(2, '0');
    }
    return hex.toUpperCase();
  }

  // Update dynamic info labels
  function updateInfoLabels() {
    if (mkValInfo) {
      mkValInfo.textContent = `(${selectedValBytes} Bytes · ${selectedValBytes * 2} Hex Characters)`;
    }
    if (mkDecInfo) {
      mkDecInfo.textContent = `(${selectedDecBytes} Bytes · ${selectedDecBytes * 2} Hex Characters)`;
    }
  }

  // Handle Preset Clicks
  mkPresetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      mkPresetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentPreset = btn.getAttribute('data-preset');

      if (currentPreset === 'net45') {
        selectValidation('HMACSHA256', 64);
        selectDecryption('AES', 32);
      } else if (currentPreset === 'net20') {
        selectValidation('SHA1', 64);
        selectDecryption('AES', 32);
      } else if (currentPreset === 'net11') {
        selectValidation('SHA1', 64);
        selectDecryption('3DES', 24);
      }
    });
  });

  function selectValidation(valName, bytes) {
    selectedValidation = valName;
    selectedValBytes = bytes;
    mkValBtns.forEach(b => {
      if (b.getAttribute('data-val') === valName && parseInt(b.getAttribute('data-bytes'), 10) === bytes) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });
    updateInfoLabels();
  }

  function selectDecryption(decName, bytes) {
    selectedDecryption = decName;
    selectedDecBytes = bytes;
    mkDecBtns.forEach(b => {
      if (b.getAttribute('data-dec') === decName && parseInt(b.getAttribute('data-bytes'), 10) === bytes) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });
    updateInfoLabels();
  }

  // Handle Validation selection
  mkValBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      selectValidation(btn.getAttribute('data-val'), parseInt(btn.getAttribute('data-bytes'), 10));
      // Switch preset to custom if user chooses custom combination
      mkPresetBtns.forEach(b => b.classList.remove('active'));
      const customBtn = document.querySelector('#mk-preset-group [data-preset="custom"]');
      if (customBtn) customBtn.classList.add('active');
      currentPreset = 'custom';
    });
  });

  // Handle Decryption selection
  mkDecBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      selectDecryption(btn.getAttribute('data-dec'), parseInt(btn.getAttribute('data-bytes'), 10));
      // Switch preset to custom
      mkPresetBtns.forEach(b => b.classList.remove('active'));
      const customBtn = document.querySelector('#mk-preset-group [data-preset="custom"]');
      if (customBtn) customBtn.classList.add('active');
      currentPreset = 'custom';
    });
  });

  // Generate Action
  if (mkGenerateBtn) {
    mkGenerateBtn.addEventListener('click', () => {
      const valKey = generateSecureHex(selectedValBytes);
      const decKey = generateSecureHex(selectedDecBytes);

      const xmlSnippet = `<!-- Place inside <system.web> in your web.config -->\n<machineKey \n  validationKey="${valKey}" \n  decryptionKey="${decKey}" \n  validation="${selectedValidation}" \n  decryption="${selectedDecryption}" \n/>`;

      if (mkXmlOutput) mkXmlOutput.textContent = xmlSnippet;
      if (mkValKeyBox) mkValKeyBox.textContent = valKey;
      if (mkDecKeyBox) mkDecKeyBox.textContent = decKey;

      if (mkValKeyCount) mkValKeyCount.textContent = `(${selectedValBytes * 2} Hex · ${selectedValBytes} Bytes)`;
      if (mkDecKeyCount) mkDecKeyCount.textContent = `(${selectedDecBytes * 2} Hex · ${selectedDecBytes} Bytes)`;

      if (mkResultsPanel) {
        mkResultsPanel.style.display = 'block';
        mkResultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  // Clear Memory Action
  if (mkClearBtn) {
    mkClearBtn.addEventListener('click', () => {
      if (mkXmlOutput) mkXmlOutput.textContent = '';
      if (mkValKeyBox) mkValKeyBox.textContent = '';
      if (mkDecKeyBox) mkDecKeyBox.textContent = '';
      if (mkResultsPanel) mkResultsPanel.style.display = 'none';
    });
  }

  // Copy helper with feedback
  function copyWithFeedback(buttonEl, textToCopy) {
    if (!textToCopy) return;
    navigator.clipboard.writeText(textToCopy).then(() => {
      const originalHtml = buttonEl.innerHTML;
      buttonEl.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> <span style="color:var(--c-green)">Copied!</span>`;
      setTimeout(() => {
        buttonEl.innerHTML = originalHtml;
      }, 2000);
    }).catch(err => {
      console.error('Copy failed:', err);
    });
  }

  if (mkCopyXmlBtn) {
    mkCopyXmlBtn.addEventListener('click', () => {
      if (mkXmlOutput) copyWithFeedback(mkCopyXmlBtn, mkXmlOutput.textContent);
    });
  }

  if (mkCopyValBtn) {
    mkCopyValBtn.addEventListener('click', () => {
      if (mkValKeyBox) copyWithFeedback(mkCopyValBtn, mkValKeyBox.textContent);
    });
  }

  if (mkCopyDecBtn) {
    mkCopyDecBtn.addEventListener('click', () => {
      if (mkDecKeyBox) copyWithFeedback(mkCopyDecBtn, mkDecKeyBox.textContent);
    });
  }
});

