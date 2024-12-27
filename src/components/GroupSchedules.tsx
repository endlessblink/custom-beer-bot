import React, { useEffect, useState, useCallback } from 'react';
import { ScheduleConfig } from './ScheduleConfig';
import { Button } from './ui/button';
import { GroupConfig, ScheduleConfig as IScheduleConfig } from '@/lib/config';
import { WhatsAppAPI } from '@/lib/whatsapp';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

interface GroupSchedulesProps {
  initialGroups?: GroupConfig[];
  onSaveGroup: (group: GroupConfig) => void;
  onRemoveGroup: (groupId: string) => void;
}

interface WhatsAppGroup {
  id: string;
  name: string;
}

export function GroupSchedules({
  initialGroups = [],
  onSaveGroup,
  onRemoveGroup,
}: GroupSchedulesProps) {
  const [groups, setGroups] = useState<GroupConfig[]>(initialGroups);
  const [availableGroups, setAvailableGroups] = useState<WhatsAppGroup[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [filteredGroups, setFilteredGroups] = useState<WhatsAppGroup[]>([]);

  // Prevent multiple simultaneous requests
  const loadAvailableGroups = useCallback(async () => {
    if (isLoading) {
      console.log('Already loading groups, skipping...');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const api = WhatsAppAPI.getInstance();
      
      // First check instance state
      console.log('Checking WhatsApp instance state...');
      const isAuthorized = await api.checkInstanceState();
      if (!isAuthorized) {
        setError('WhatsApp instance is not authorized. Please scan the QR code in the Green API dashboard.');
        setAvailableGroups([]);
        return;
      }

      // Then fetch groups
      console.log('Fetching WhatsApp groups...');
      const whatsappGroups = await api.getGroups();
      
      if (!whatsappGroups || whatsappGroups.length === 0) {
        console.log('No groups found');
        setAvailableGroups([]);
        setError('No WhatsApp groups found. Make sure you are an admin of at least one group.');
        return;
      }

      console.log('Available groups:', whatsappGroups);
      
      // Filter out groups that are already added
      const availableGroups = whatsappGroups.filter(
        group => !groups.some(g => g.groupId === group.id)
      );
      console.log('Filtered available groups:', availableGroups);
      
      setAvailableGroups(availableGroups);
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to load groups';
      console.error('Error loading groups:', error);
      setError(errorMessage);
      setAvailableGroups([]);
    } finally {
      setIsLoading(false);
    }
  }, [groups, isLoading]);

  // Load groups only once on initial mount
  useEffect(() => {
    if (isInitialLoad) {
      loadAvailableGroups();
      setIsInitialLoad(false);
    }
  }, [isInitialLoad, loadAvailableGroups]);

  // Update groups when initialGroups changes
  useEffect(() => {
    setGroups(initialGroups);
  }, [initialGroups]);

  // Separate effect for syncing names
  useEffect(() => {
    if (initialGroups.length > 0 && !isLoading) {
      const syncNames = async () => {
        try {
          const api = WhatsAppAPI.getInstance();
          const allGroups = await api.getGroups();
          
          // Update names for existing groups
          const updatedGroups = initialGroups.map(group => {
            const match = allGroups.find(g => g.id === group.groupId);
            return match ? { ...group, name: match.name } : group;
          });

          setGroups(updatedGroups);
        } catch (error) {
          // Don't show error for name sync, just log it
          console.warn('Failed to sync group names:', error);
        }
      };

      syncNames();
    }
  }, [initialGroups, isLoading]);

  const handleRefresh = useCallback(async () => {
    setIsInitialLoad(true);
  }, []);

  const syncGroupNames = async () => {
    if (isLoading) {
      console.log('Already loading, skipping sync...');
      return;
    }

    try {
      const api = WhatsAppAPI.getInstance();
      const whatsappGroups = await api.getGroups();
      
      if (!whatsappGroups || whatsappGroups.length === 0) {
        console.log('No groups received during sync');
        return;
      }

      // Update names of existing groups
      const updatedGroups = groups.map(group => {
        const whatsappGroup = whatsappGroups.find(wg => wg.id === group.groupId);
        if (whatsappGroup && whatsappGroup.name !== group.name) {
          const updatedGroup = { ...group, name: whatsappGroup.name };
          onSaveGroup(updatedGroup);
          return updatedGroup;
        }
        return group;
      });

      setGroups(updatedGroups);
    } catch (error) {
      console.error('Failed to sync group names:', error);
    }
  };

  const handleAddGroup = (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedGroupId) return;

    const selectedGroup = availableGroups.find(g => g.id === selectedGroupId);
    if (!selectedGroup) return;

    const newGroup: GroupConfig = {
      groupId: selectedGroup.id,
      name: selectedGroup.name,
      schedule: {
        frequency: 'daily',
        time: '20:00',
        enabled: true,
      },
    };

    onSaveGroup(newGroup);
    setSelectedGroupId('');
    loadAvailableGroups();
  };

  const handleUpdateSchedule = (groupId: string, schedule: IScheduleConfig) => {
    const group = groups.find(g => g.groupId === groupId);
    if (group) {
      const updatedGroup = { ...group, schedule };
      onSaveGroup(updatedGroup);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Add WhatsApp Group</h2>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Refresh'}
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-400 p-4 my-4">
          <p className="text-red-700">{error}</p>
          <p className="text-sm text-red-600 mt-1">
            Make sure your WhatsApp instance is authorized and you have admin access to at least one group.
          </p>
        </div>
      )}

      <form onSubmit={handleAddGroup} className="flex gap-4 items-end">
        <div className="flex-1 space-y-2">
          <label className="text-sm font-medium">Add WhatsApp Group</label>
          <div className="relative">
            <Select
              value={selectedGroupId}
              onValueChange={setSelectedGroupId}
              disabled={isLoading}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder={isLoading ? "Loading groups..." : error ? "Error loading groups" : "Select a group"} />
              </SelectTrigger>
              <SelectContent className="max-h-[300px] overflow-y-auto">
                <div className="sticky top-0 bg-white p-2 border-b">
                  <input
                    type="text"
                    placeholder="Search groups..."
                    className="w-full px-2 py-1 border rounded text-sm"
                    onChange={(e) => {
                      const searchTerm = e.target.value.toLowerCase();
                      const filtered = availableGroups.filter(group =>
                        group.name.toLowerCase().includes(searchTerm) ||
                        group.id.toLowerCase().includes(searchTerm)
                      );
                      setFilteredGroups(filtered);
                    }}
                  />
                </div>
                {(filteredGroups || availableGroups).map((group) => (
                  <SelectItem key={group.id} value={group.id}>
                    {group.name} ({group.id})
                  </SelectItem>
                ))}
                {availableGroups.length === 0 && !isLoading && !error && (
                  <SelectItem value="none" disabled>
                    No available groups
                  </SelectItem>
                )}
                {error && (
                  <SelectItem value="error" disabled>
                    {error}
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
            {isLoading && (
              <div className="absolute right-10 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
              </div>
            )}
          </div>
        </div>
        <Button 
          type="submit" 
          disabled={!selectedGroupId || isLoading}
        >
          Add Group
        </Button>
        <Button 
          type="button"
          variant="outline"
          onClick={() => {
            loadAvailableGroups();
            syncGroupNames();
          }}
          disabled={isLoading}
        >
          🔄 Refresh
        </Button>
      </form>

      <div className="space-y-6">
        {groups.map((group) => (
          <div key={group.groupId} className="relative bg-white rounded-lg shadow-sm border p-4">
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-2 top-2"
              onClick={() => onRemoveGroup(group.groupId)}
            >
              ×
            </Button>
            <div className="mb-2">
              <h3 className="text-lg font-semibold">{group.name}</h3>
              <p className="text-sm text-gray-500 dir-ltr">ID: {group.groupId}</p>
            </div>
            <ScheduleConfig
              groupId={group.groupId}
              initialConfig={group.schedule}
              onSave={(schedule) => handleUpdateSchedule(group.groupId, schedule)}
            />
          </div>
        ))}
      </div>

      {groups.length === 0 && (
        <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
          No groups configured. Add a WhatsApp group to get started.
        </div>
      )}
    </div>
  );
}