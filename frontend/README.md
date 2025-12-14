# Digital Ethics Monitor - Frontend

Modern ve güvenli bir arayüz ile AI etik izleme sistemi.

## 🎨 Özellikler

- **JWT Authentication**: Güvenli kullanıcı kimlik doğrulama
- **Real-time Dashboard**: Canlı AI karar izleme ve metrikler
- **Bias Detection Visualization**: Chart.js ile interaktif grafikler
- **Admin Panel**: Sistem logları ve raporlar için yönetim paneli
- **Responsive Design**: Tüm cihazlarda uyumlu modern tasarım
- **Dark Theme**: Profesyonel görünüm için koyu tema
- **Glassmorphism Effects**: Modern UI tasarım efektleri

## 📁 Dosya Yapısı

```
frontend/
├── index.html              # Login sayfası
├── dashboard.html          # Ana dashboard
├── admin.html              # Admin panel
├── css/
│   └── styles.css          # Custom CSS stilleri
└── js/
    ├── api.js              # Backend API client
    ├── auth.js             # Authentication yönetimi
    ├── charts.js           # Chart.js görselleştirmeleri
    └── main.js             # Ana uygulama mantığı
```

## 🚀 Kurulum

### 1. Basit HTTP Server ile Çalıştırma

Python 3 ile:
```bash
cd frontend
python -m http.server 8080
```

Tarayıcıda açın: `http://localhost:8080`

### 2. Live Server (VS Code Extension)

1. VS Code'da "Live Server" extension'ını yükleyin
2. `index.html` dosyasına sağ tıklayın
3. "Open with Live Server" seçin

## 🔌 Backend Entegrasyonu

### API Endpoint'leri

Tüm API çağrıları şu anda **placeholder** fonksiyonlarla temsil edilmektedir. 
Backend hazır olduğunda `js/api.js` dosyasındaki fonksiyonları güncelleyin:

```javascript
// Şu anki durum (Placeholder)
async function loginUser(email, password) {
    console.log('LOGIN API CALL (Placeholder)');
    return Promise.resolve({ token: 'placeholder_token' });
}

// Backend hazır olduğunda
async function loginUser(email, password) {
    return api.post('/auth/login', { email, password }, { auth: false });
}
```

### Güncellenecek API Endpoint'leri

1. **Authentication**
   - `POST /auth/login` - Kullanıcı girişi
   - `POST /auth/logout` - Kullanıcı çıkışı
   - `POST /auth/refresh` - Token yenileme

2. **Dashboard**
   - `GET /dashboard/stats` - Dashboard istatistikleri
   - `GET /decisions` - AI kararları listesi
   - `GET /analytics/bias` - Bias analiz verileri
   - `GET /analytics/fairness` - Fairness metrikleri

3. **Admin**
   - `GET /admin/logs` - Sistem logları
   - `GET /admin/reports` - AI karar raporları
   - `GET /admin/reports/:id/download` - Rapor indirme

### Backend URL Ayarı

`js/api.js` dosyasında backend URL'ini güncelleyin:

```javascript
const API_BASE_URL = 'http://localhost:8000/api';  // Backend URL'inize göre değiştirin
```

## 🎯 Kullanım

### Login Sayfası

1. Tarayıcıda `index.html` sayfasını açın
2. Email ve şifre girin
3. "Beni Hatırla" seçeneği ile token'ı localStorage'a kaydedin
4. Başarılı giriş sonrası otomatik olarak dashboard'a yönlendirilirsiniz

**Not**: Şu anda herhangi bir email/şifre ile giriş yapabilirsiniz (placeholder mode).

### Dashboard

Dashboard'da şunları görebilirsiniz:
- Toplam karar sayısı
- Tespit edilen bias sayısı
- Adalet skoru
- Sistem sağlığı
- Bias dağılım grafiği
- Fairness metrikleri (radar chart)
- Karar zaman çizelgesi
- Son kararlar tablosu

### Admin Panel

Admin panelinde:
- Sistem loglarını filtreleyebilirsiniz
- AI karar raporlarını görüntüleyebilirsiniz
- Raporları indirebilirsiniz
- Pagination ile sayfalama yapabilirsiniz

## 🔒 Güvenlik

### JWT Token Yönetimi

- Token'lar localStorage'da saklanır
- Her API isteğinde otomatik olarak `Authorization` header'ına eklenir
- 401 response'da otomatik logout ve login sayfasına yönlendirme
- Token validation ve refresh mekanizması hazır (backend entegrasyonu sonrası aktif olacak)

### RBAC (Role-Based Access Control)

- Admin sayfasına sadece `admin` role'üne sahip kullanıcılar erişebilir
- `auth.js` içinde `isAdmin()` fonksiyonu ile kontrol edilir
- Protected route guard `requireAuth()` ile sayfa koruması

## 🎨 Tasarım

### Teknolojiler

- **HTML5**: Semantik yapı
- **Tailwind CSS**: Utility-first CSS framework (CDN)
- **Custom CSS**: Glassmorphism, animations, dark theme
- **Chart.js**: Veri görselleştirme
- **Google Fonts (Inter)**: Modern tipografi

### Renk Paleti

```css
--color-primary: #8b5cf6    /* Purple */
--color-secondary: #3b82f6  /* Blue */
--color-success: #10b981    /* Green */
--color-warning: #f59e0b    /* Yellow */
--color-danger: #ef4444     /* Red */
```

### Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 📊 Chart Özelleştirme

Chart.js konfigürasyonları `js/charts.js` dosyasında bulunur:

- **Bias Chart**: Bar chart - Demographic parity dağılımı
- **Fairness Chart**: Radar chart - Equalized odds, demographic parity vb.
- **Timeline Chart**: Line chart - Zaman içinde karar trendi

## 🔄 Auto-Refresh

Dashboard otomatik olarak her 30 saniyede bir güncellenir:
- Dashboard istatistikleri
- Grafikler
- Son kararlar tablosu

Auto-refresh ayarını `js/main.js` içinde değiştirebilirsiniz:

```javascript
setInterval(async () => {
    // Refresh logic
}, 30000); // 30 seconds
```

## 🐛 Debugging

Tüm API çağrıları console'da loglanır:

```javascript
console.log('LOGIN API CALL (Placeholder):', { email, password });
```

Chrome DevTools'u açın (F12) ve Network/Console tab'larını kontrol edin.

## 📝 TODO

### Backend Entegrasyonu Sonrası

- [ ] `api.js` içindeki placeholder fonksiyonları gerçek API çağrılarıyla değiştir
- [ ] JWT token expiration kontrolü ekle
- [ ] Token refresh mekanizmasını aktif et
- [ ] CORS ayarlarını backend ile eşleştir
- [ ] Error handling'i backend response'larına göre güncelle
- [ ] Gerçek veri ile chart testleri yap
- [ ] Admin panelinde rapor indirme fonksiyonunu tamamla

### İyileştirmeler

- [ ] Loading states ekle (skeleton screens)
- [ ] Toast notifications ekle (başarı/hata mesajları)
- [ ] Form validation güçlendir
- [ ] Accessibility (ARIA) iyileştirmeleri
- [ ] PWA desteği ekle
- [ ] Unit testler yaz

## 🤝 Katkıda Bulunma

1. Backend API'yi tamamlayın
2. `js/api.js` dosyasındaki TODO yorumlarını takip edin
3. Her endpoint için gerçek API çağrısını implement edin
4. Test edin ve güvenlik kontrollerini yapın

## 📄 Lisans

Bu proje "Digital Ethics Monitor - Secure Computing Project" kapsamında geliştirilmiştir.

---

**DEM v1.0** | Secure & Transparent AI Framework
