import React from 'react';
import { Shield, PhoneCall, Radio, CheckCircle, ExternalLink, AlertTriangle, FileText, Globe } from 'lucide-react';

export default function GovernmentFooter() {
  return (
    <footer className="govt-footer">
      {/* Top Emergency Contacts Bar */}
      <div className="govt-footer-emergency-bar">
        <div className="emergency-bar-inner">
          <div className="emergency-title">
            <PhoneCall size={16} className="text-amber-400 animate-pulse" />
            <span>24x7 NATIONAL DISASTER EMERGENCY HELPLINES (TOLL FREE):</span>
          </div>
          <div className="emergency-numbers-grid">
            <a href="tel:112" className="emergency-badge">
              <span className="badge-num">112</span>
              <span className="badge-label">National Emergency (ERSS)</span>
            </a>
            <a href="tel:1070" className="emergency-badge">
              <span className="badge-num">1070</span>
              <span className="badge-label">NDMA Disaster Relief HQ</span>
            </a>
            <a href="tel:1077" className="emergency-badge">
              <span className="badge-num">1077</span>
              <span className="badge-label">ASDMA SEOC / SDRF Assam</span>
            </a>
            <a href="tel:1078" className="emergency-badge">
              <span className="badge-num">1078</span>
              <span className="badge-label">NDRF Emergency Operations</span>
            </a>
          </div>
        </div>
      </div>

      {/* Main Footer Directory */}
      <div className="govt-footer-main">
        <div className="footer-grid">
          {/* Col 1: Government Identity & Mission */}
          <div className="footer-col">
            <div className="govt-emblem-lockup">
              <div className="emblem-symbol">
                <img src="/logo-shield-transparent.png" alt="TERRA SHIELD Logo" className="govt-emblem-img" />
              </div>
              <div>
                <div className="govt-ministry-text">ENVIRONMENTAL HAZARD SENSING & MESH RELAY</div>
                <div className="govt-org-text">TERRA SHIELD NETWORK</div>
                <div className="govt-sub-text">Smart India Hackathon • SIH26178</div>
              </div>
            </div>
            <p className="footer-desc">
              TERRA SHIELD is an integrated multi-hazard early warning and environmental monitoring network designed for 
              complex riverine terrains of the Brahmaputra & Kopili basins (Assam 16 June Incident), combining real-time edge telemetry, 
              resilient decentralized LoRa mesh networking, and vernacular ground truth verification.
            </p>
            <div className="footer-meta-pill">
              <span className="status-dot"></span>
              <span>Common Alerting Protocol (CAP) ITU-T X.1303 Compliant</span>
            </div>
          </div>

          {/* Col 2: Inter-Agency Integrated Feeds */}
          <div className="footer-col">
            <h4 className="footer-heading">INTEGRATED DATA AGENCIES</h4>
            <ul className="footer-links-list">
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>CWC Central Water Commission</strong>
                  <div className="link-sub">Real-time Brahmaputra & Kopili river gauge & flood breach telemetry</div>
                </div>
              </li>
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>IMD India Meteorological Dept</strong>
                  <div className="link-sub">Doppler radar precipitation & 2-year calibrated monsoonal forecasting</div>
                </div>
              </li>
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>ASDMA Assam State Disaster Authority</strong>
                  <div className="link-sub">State Emergency Operations Center (1070) & evacuation coordination</div>
                </div>
              </li>
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>CPCB Central Pollution Board</strong>
                  <div className="link-sub">Continuous ambient AQI sentinels (PM2.5 / PM10 monitoring)</div>
                </div>
              </li>
            </ul>
          </div>

          {/* Col 3: Basin Network Specifications */}
          <div className="footer-col">
            <h4 className="footer-heading">BASIN SENSOR GRID STATUS</h4>
            <div className="basin-specs">
              <div className="spec-item">
                <span className="spec-label">Target Basin:</span>
                <span className="spec-value">Brahmaputra - Kopili - Barak River Basin, Assam</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Node Grid:</span>
                <span className="spec-value">20 Distributed Hardware & Edge Telemetry Sentinels</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Mesh Frequency:</span>
                <span className="spec-value">868 MHz LoRaWAN Multi-Hop Decentralized P2P</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Failover Architecture:</span>
                <span className="spec-value">Autonomous Cellular Blackout LittleFS Flash Buffer</span>
              </div>
              <div className="spec-item">
                <span className="spec-label">Human Verification:</span>
                <span className="spec-value">Automated WhatsApp AI Bot for Village Gaonburahs & Sarpanches</span>
              </div>
            </div>
          </div>

          {/* Col 4: Public Safety Guidelines */}
          <div className="footer-col">
            <h4 className="footer-heading">DISASTER PROTOCOLS & DO'S/DON'TS</h4>
            <ul className="footer-links-list">
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>Flash Flood & Embankment Breach:</strong>
                  <div className="link-sub">Evacuate riverfront embankments immediately; proceed to higher ground.</div>
                </div>
              </li>
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>Slope Failure & Landslide Protocol:</strong>
                  <div className="link-sub">Clear unstable foothill mud banks; avoid saturated leeward slopes.</div>
                </div>
              </li>
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>Safe Evacuation Camps:</strong>
                  <div className="link-sub">Kampur HS Camp, Cotton Collegiate HS, Raha College Relief Hub.</div>
                </div>
              </li>
              <li>
                <span className="bullet">›</span>
                <div>
                  <strong>Offline Citizen Radio & SOS:</strong>
                  <div className="link-sub">Tune to All India Radio 102.3 FM & local wireless mesh alert beacons.</div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Legal & Compliance Strip */}
        <div className="footer-bottom-bar">
          <div className="copyright-text">
            © 2026 TERRA SHIELD • Built for Smart India Hackathon (SIH26178) • In compliance with National Disaster Management Act 2005.
          </div>
          <div className="compliance-links">
            <span>Common Alerting Protocol (CAP) ITU-T X.1303</span>
            <span className="divider">•</span>
            <span>Open Geospatial Consortium (OGC) Standards</span>
            <span className="divider">•</span>
            <span>Decentralized LittleFS Buffering</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
