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
- 🔄 Manual refresh button with cooldown
- 📱 Responsive design

## Setup

1. **Install dependencies** (if not already done):
   ```bash
   pnpm i
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to set your FastAPI URL:PORT if not using default
   ```

3. **Start the development server**:
   ```bash
   pnpm start
   ```

4. **Build for production**:
   ```bash
   pnpm run build
   ```

## Usage

1. **Authentication**: Enter your Life360 Bearer token on the login screen
2. **Select Circle**: Use the dropdown to switch between circles
3. **View Members**: Active members appear as markers on the map
4. **Change Map Style**: Select between light, dark, and satellite modes (MapBox API Key required for satellite)
5. **Member Details**: Click on any marker to see detailed information
6. **Refresh**: Click the refresh button or wait for auto-refresh

## Marker Features

- **Profile Pictures**: Members with avatars show their photo
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

## Troubleshooting

- **Map not loading**: Check console for errors, ensure API is running
- **No members shown**: Verify members have location sharing enabled
- **Authentication fails**: Ensure token includes "Bearer " prefix
- **CORS errors**: Check API CORS configuration