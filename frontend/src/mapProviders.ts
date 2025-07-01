// mapProviders.ts - Map tile provider configurations

export interface TileProvider {
  name: string;
  url: string;
  attribution: string;
  maxZoom?: number;
  subdomains?: string | string[];
  accessToken?: string;
}

export const tileProviders: Record<string, TileProvider> = {
  mapboxSatellite: {
    name: "Mapbox Satellite",
    url: "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token={accessToken}",
    attribution:
      '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; OSM contributors',
    maxZoom: 22,
    accessToken: process.env.REACT_APP_MAPBOX_TOKEN || "",
  },

  cartoDark: {
    name: "CartoDB Dark Matter",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
    subdomains: "abcd",
  },

  cartoLight: {
    name: "CartoDB Light",
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    maxZoom: 19,
    subdomains: "abcd",
  },
};

// Helper function to get tile URL with token replaced
export const getTileUrl = (provider: TileProvider): string => {
  if (provider.accessToken) {
    return provider.url.replace("{accessToken}", provider.accessToken);
  }
  return provider.url;
};
