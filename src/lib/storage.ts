import { GroupConfig } from './config';

const STORAGE_KEY = 'whatsapp-summary-groups';

export const storage = {
  getGroups: (): GroupConfig[] => {
    if (typeof window === 'undefined') return [];
    
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to load groups from storage:', error);
      return [];
    }
  },

  saveGroup: (group: GroupConfig): void => {
    if (typeof window === 'undefined') return;

    try {
      const groups = storage.getGroups();
      const existingIndex = groups.findIndex(g => g.groupId === group.groupId);
      
      if (existingIndex >= 0) {
        groups[existingIndex] = group;
      } else {
        groups.push(group);
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(groups));
    } catch (error) {
      console.error('Failed to save group to storage:', error);
    }
  },

  removeGroup: (groupId: string): void => {
    if (typeof window === 'undefined') return;

    try {
      const groups = storage.getGroups();
      const updatedGroups = groups.filter(g => g.groupId !== groupId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedGroups));
    } catch (error) {
      console.error('Failed to remove group from storage:', error);
    }
  },

  clearGroups: (): void => {
    if (typeof window === 'undefined') return;
    
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear groups from storage:', error);
    }
  }
}; 