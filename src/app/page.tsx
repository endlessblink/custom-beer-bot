'use client';

import { useEffect, useState } from 'react';
import { GroupSchedules } from '@/components/GroupSchedules';
import { GroupConfig } from '@/lib/config';
import { storage } from '@/lib/storage';
import { useToast } from '@/components/ui/toast-context';

const GROUP_ID_REGEX = /^\d+@g\.us$/;

export default function Home() {
  const [isLoading, setIsLoading] = useState(true);
  const [groups, setGroups] = useState<GroupConfig[]>([]);
  const { addToast } = useToast();

  useEffect(() => {
    // Load saved groups on mount
    const savedGroups = storage.getGroups();
    setGroups(savedGroups);
    setIsLoading(false);
  }, []);

  const validateGroupId = (groupId: string): boolean => {
    if (!GROUP_ID_REGEX.test(groupId)) {
      addToast({
        title: 'Invalid Group ID',
        description: 'Please select a group from the dropdown list.',
        variant: 'destructive',
      });
      return false;
    }

    const exists = groups.some(g => g.groupId === groupId);
    if (exists) {
      addToast({
        title: 'Group Already Exists',
        description: 'This group has already been added',
        variant: 'destructive',
      });
      return false;
    }

    return true;
  };

  const handleSaveGroup = (group: GroupConfig) => {
    if (!validateGroupId(group.groupId)) return;

    try {
      storage.saveGroup(group);
      setGroups(storage.getGroups());
      addToast({
        title: 'Success',
        description: 'Group configuration saved successfully',
      });
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to save group configuration',
        variant: 'destructive',
      });
    }
  };

  const handleRemoveGroup = (groupId: string) => {
    try {
      storage.removeGroup(groupId);
      setGroups(storage.getGroups());
      addToast({
        title: 'Success',
        description: 'Group removed successfully',
      });
    } catch (error) {
      addToast({
        title: 'Error',
        description: 'Failed to remove group',
        variant: 'destructive',
      });
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen p-8">
        <div className="max-w-4xl mx-auto">
          Loading...
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">WhatsApp Group Summary Bot</h1>
          <p className="text-gray-600">Configure your group message summary schedules</p>
        </div>

        <GroupSchedules
          initialGroups={groups}
          onSaveGroup={handleSaveGroup}
          onRemoveGroup={handleRemoveGroup}
        />
      </div>
    </main>
  );
}
