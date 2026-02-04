# Offline-First PWA Architecture: Punto 3 Resilience

The OnTrackIA platform is designed for "Punto 3" resilience, allowing técnicos to operate at 100% capacity in hangars or flight lines without internet connectivity.

## 📶 Connectivity Management

### Reactive Sync Indicator

The UI features a dynamic visual indicator (Green/Red dot) in the Header that reflects real-time network status.

- **Green**: Connected to backend. Sync active.
- **Red**: Offline. Data is being persisted locally.

### Sync Logic (Header.jsx & index.css)

- **Status Detection**: Uses `window.addEventListener('online')` and `('offline')`.
- **UI Implementation**: A `:before` or `:after` pseudo-element with a glowing animation to indicate activity.

## 💾 Local Persistence (Dexie.js / IndexedDB)

All critical data (OJT tasks, trainee profiles, pending signatures) is stored in the browser's IndexedDB using **Dexie.js**.

- **Schema Definition (`schema.ts`)**: Defines multi-tenant tables for local operation.
- **Offline Operations**: Creating or updating records happens first in the local DB.
- **Sync Engine**: Once connection is restored, the `SyncEngine` orchestrates background uploads with:
  - **Retry Policy**: Exponential backoff for failed transfers.
  - **Circuit Breaker**: Prevents overwhelming the server during instability.

## 📱 Mobile Adaptation

- **Vertical Stacking**: Dashboard cards (stats, trainee lists) stack vertically on small screens.
- **Touch Ergonomics**: All actionable icons (Eye, Lock, AI-Assist) maintain a **44x44px** minimum touch target.
- **Viewport Fit**: `viewport-fit=cover` ensures the UI adapts to modern mobile screen geometries.
