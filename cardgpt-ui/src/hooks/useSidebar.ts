import { create } from 'zustand';

interface SidebarState {
  isOpen: boolean;
  isMobile: boolean;
  toggleSidebar: () => void;
  closeSidebar: () => void;
  openSidebar: () => void;
  setMobile: (isMobile: boolean) => void;
}

export const useSidebar = create<SidebarState>((set) => ({
  isOpen: true, // Default to open on desktop
  isMobile: false,
  
  toggleSidebar: () => set((state) => ({ isOpen: !state.isOpen })),
  closeSidebar: () => set({ isOpen: false }),
  openSidebar: () => set({ isOpen: true }),
  setMobile: (isMobile: boolean) => set({ 
    isMobile, 
    isOpen: !isMobile // Close sidebar by default on mobile
  }),
}));