# Life360 Map Tracker - Frontend

A React TypeScript application that displays Life360 members on an interactive map using Leaflet.

## Features

- 🔐 Secure token-based authentication
- 🗺️ Interactive map display using OpenStreetMap
- 👥 Circle selection to view different groups
- 📍 Real-time member location display
- 🖼️ Custom markers with profile pictures
- 🔋 Battery level indicators
- 🚗 Driving status indicators
- 🔄 Auto-refresh every 30 seconds
- 📱 Responsive design

## Setup

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to set your API URL if not using default
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## File Structure

```
frontend/src/
├── components/
│   ├── Auth.tsx           # Authentication form
│   ├── Auth.css          
│   ├── MapView.tsx        # Main map component
│   ├── MapView.css       
│   ├── CircleSelector.tsx # Circle dropdown selector
│   ├── CircleSelector.css
│   ├── MemberMarker.tsx   # Custom map markers
│   └── MemberMarker.css  
├── api.ts                 # API service layer
├── types.ts               # TypeScript interfaces
├── App.tsx                # Main app component
├── App.css               
└── index.tsx              # Entry point
```

## Usage

1. **Authentication**: Enter your Life360 Bearer token on the login screen
2. **Select Circle**: Use the dropdown to switch between circles
3. **View Members**: Active members appear as markers on the map
4. **Member Details**: Click on any marker to see detailed information
5. **Refresh**: Click the refresh button or wait for auto-refresh

## Marker Features

- **Profile Pictures**: Members with avatars show their photo
- **Default Icons**: Members without avatars show initials
- **Driving Indicator**: 🚗 emoji appears for driving members
- **Popup Information**: 
  - Full name and status
  - Current address/location name
  - Battery level (color-coded)
  - Last update time
  - Phone number (clickable)

## Security

- Token is stored in localStorage
- Token is only sent to your configured API server
- Automatic logout on invalid token

## Customization

### Change Map Provider
Edit `MapView.tsx` to use a different tile provider:
```tsx
<TileLayer
  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  attribution='...'
/>
```

### Adjust Refresh Interval
In `MapView.tsx`, change the interval (in milliseconds):
```tsx
const interval = setInterval(() => {
  refreshMembers();
}, 30000); // 30 seconds
```

### Customize Markers
Modify `MemberMarker.tsx` to change marker appearance or popup content.

## Troubleshooting

- **Map not loading**: Check console for errors, ensure API is running
- **No members shown**: Verify members have location sharing enabled
- **Authentication fails**: Ensure token includes "Bearer " prefix
- **CORS errors**: Check API CORS configuration