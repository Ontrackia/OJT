# 🚀 OnTrackIA V1-Core - Deployment & Testing Guide

**Version:** 1.0 Production  
**Date:** 2026-02-04  
**Status:** Ready for Deployment

---

## 📋 QUICK START

### **Local Testing:**

```bash
cd /Users/gregorioromerovega/Desktop/OnTrackIA_OJT

# 1. Run pre-flight tests
./test_preflight.sh

# 2. Build and prepare
./deploy_local.sh
```

### **Production Deployment:**

```bash
# On Hetzner server
./deploy_hetzner.sh
```

---

## 🎯 DEPLOYMENT SCRIPTS

### **1. `deploy_local.sh`**

**Purpose:** Local build and preparation

**What it does:**

- Installs npm dependencies
- Runs security audit
- Builds production frontend
- Checks Python environment
- Verifies PostgreSQL connection
- Generates deployment instructions

**Run:**

```bash
chmod +x deploy_local.sh
./deploy_local.sh
```

### **2. `deploy_hetzner.sh`**

**Purpose:** Full Hetzner server deployment

**What it does:**

- Installs system dependencies
- Configures PostgreSQL
- Sets up Python environment
- Applies database migrations
- Creates systemd services
- Configures Nginx + SSL
- Sets up fail2ban security
- Configures daily backups

**Run on server:**

```bash
chmod +x deploy_hetzner.sh
sudo ./deploy_hetzner.sh
```

### **3. `test_preflight.sh`**

**Purpose:** Pre-deployment testing

**What it does:**

- Tests backend health endpoints
- Verifies API endpoints
- Tests SMS Quick Report
- Checks Master Audit Log
- Provides manual test checklist

**Run:**

```bash
chmod +x test_preflight.sh
./test_preflight.sh
```

---

## 🧪 MANUAL TESTING CHECKLIST

### **Phase 1: Offline Mode Test**

- [ ] Open application in Chrome/Firefox
- [ ] Open DevTools > Application > Service Workers
- [ ] Enable "Offline" mode
- [ ] Create a finding with description
- [ ] Use voice dictation (click mic button)
- [ ] Upload evidence photo
- [ ] Disable "Offline" mode
- [ ] Verify sync indicator shows "Syncing..."
- [ ] Check PostgreSQL for synced data
- [ ] Verify SHA-256 hash integrity

### **Phase 2: Voice-to-Text Test**

- [ ] Open finding form
- [ ] Click microphone button (should turn red)
- [ ] Dictate in Spanish: "Hallazgo crítico. Punto y aparte. Nueva línea. Coma."
- [ ] Verify text formatting
- [ ] Switch to English (EN button)
- [ ] Dictate: "Critical finding. Period. New line. Comma."
- [ ] Verify English formatting

### **Phase 3: Bilingual Interface Test**

- [ ] Click ES/EN selector in header
- [ ] Verify all UI text changes
- [ ] Check login page translations
- [ ] Check dashboard translations
- [ ] Reload page
- [ ] Verify language persists (localStorage)

### **Phase 4: Theme Toggle Test**

- [ ] Click theme toggle (sun/moon icon)
- [ ] Verify CSS variables change
- [ ] Check dark mode colors
- [ ] Check light mode colors
- [ ] Test at night (should auto-enable NVIS)
- [ ] Reload page
- [ ] Verify theme persists

### **Phase 5: SMS Just Culture Test**

- [ ] Go to login page (not logged in)
- [ ] Click "Reporte Voluntario SMS" button
- [ ] Fill out form anonymously
- [ ] Upload evidence
- [ ] Select severity
- [ ] Submit report
- [ ] Verify success message
- [ ] Check database for anonymous report
- [ ] Verify IP is hashed (not plain text)

### **Phase 6: Master Audit Log Test**

- [ ] Login as admin
- [ ] Create audit context
- [ ] Add finding
- [ ] Add RCA
- [ ] Upload evidence
- [ ] Generate PDF
- [ ] Verify SHA-256 hash in PDF footer
- [ ] Check Master Audit Log
- [ ] Verify all actions logged
- [ ] Try to modify audit log (should fail)

### **Phase 7: Evidence Vault Test**

- [ ] Upload image (>2MB)
- [ ] Verify compression to <2MB
- [ ] Check SHA-256 hash
- [ ] Verify AES-256 encryption
- [ ] Download evidence
- [ ] Verify decryption works
- [ ] Check 5-year retention metadata

### **Phase 8: AI Governance Test**

- [ ] Generate RCA with AI
- [ ] Verify "AI-Generated" badge
- [ ] Verify HITL validation required
- [ ] Try to close audit without validation
- [ ] Should show warning
- [ ] Validate AI suggestion
- [ ] Verify audit can now close

---

## 🔧 TROUBLESHOOTING

### **Frontend not building:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### **Backend not starting:**

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python rag_server_mistral.py
```

### **PostgreSQL connection failed:**

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string in .env
cat .env | grep DATABASE_URL
```

### **SSL certificate issues:**

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## 📊 PRODUCTION URLS

**After deployment, verify:**

- **Frontend:** <https://ontrackia.com>
- **Backend API:** <https://ontrackia.com/api/v2>
- **API Docs:** <https://ontrackia.com/docs>
- **Health Check:** <https://ontrackia.com/health>

---

## 🎯 SUCCESS CRITERIA

OnTrackIA V1-Core is **100% READY** when:

1. ✅ All automated tests pass
2. ✅ All manual tests pass
3. ✅ SSL certificate valid
4. ✅ Offline mode works
5. ✅ Voice dictation works
6. ✅ Bilingual interface works
7. ✅ Theme toggle works
8. ✅ SMS Just Culture accessible
9. ✅ Master Audit Log immutable
10. ✅ Evidence Vault encrypted

---

**Status:** READY FOR DEPLOYMENT 🚀  
**Next:** Execute deployment scripts and run tests
